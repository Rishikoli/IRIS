import os
import hashlib
import time
import asyncio
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import tempfile
import json

try:
    import pytesseract
    import PIL.Image
    from pdf2image import convert_from_path
    import PyPDF2
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

from pydantic import BaseModel
from app.services.gemini_service import GeminiService
from app.services.enhanced_document_validation import enhanced_document_validator, DocumentValidationResult
from app.services.fmp_service import fmp_service

class PDFAnomalyResult(BaseModel):
    type: str  # 'metadata', 'font', 'signature', 'content', 'structure'
    severity: str  # 'low', 'medium', 'high'
    description: str
    details: Dict = {}

class PDFAnalysisResult(BaseModel):
    file_hash: str
    filename: str
    file_size: int
    ocr_text: Optional[str] = None
    anomalies: List[PDFAnomalyResult] = []
    score: int  # 0-100 authenticity score
    is_likely_fake: bool
    processing_time_ms: int
    gemini_analysis: Optional[Dict] = None
    enhanced_validation: Optional[DocumentValidationResult] = None

class PDFAnalysisService:
    def __init__(self):
        self.gemini_service = GeminiService()
        self.temp_dir = Path(tempfile.gettempdir()) / "iris_pdf_analysis"
        self.temp_dir.mkdir(exist_ok=True)
        
        # Configure tesseract path if needed (Windows)
        if os.name == 'nt':  # Windows
            tesseract_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                r"C:\Users\{}\AppData\Local\Tesseract-OCR\tesseract.exe".format(os.getenv('USERNAME', ''))
            ]
            for path in tesseract_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    break
    
    async def analyze_pdf(self, file_path: str, filename: str) -> PDFAnalysisResult:
        """Comprehensive PDF analysis for authenticity"""
        start_time = time.time()
        
        # Calculate file hash and size
        file_hash = await self._calculate_file_hash(file_path)
        file_size = os.path.getsize(file_path)
        
        # Initialize result
        result = PDFAnalysisResult(
            file_hash=file_hash,
            filename=filename,
            file_size=file_size,
            score=50,  # Default neutral score
            is_likely_fake=False,
            processing_time_ms=0
        )
        
        try:
            # Extract text using OCR
            if OCR_AVAILABLE:
                result.ocr_text = await self._extract_text_ocr(file_path)
            else:
                result.ocr_text = await self._extract_text_fallback(file_path)
            
            # Detect anomalies
            anomalies = await self._detect_anomalies(file_path, result.ocr_text or "")
            result.anomalies = anomalies
            
            # Analyze with Gemini (always attempt, even if OCR is empty)
            if result.ocr_text and len(result.ocr_text.strip()) > 10:
                result.gemini_analysis = await self._analyze_with_gemini(result.ocr_text, filename)
            else:
                # Compose a surrogate context including anomalies and a hint about missing OCR
                anomalies_summary = "\n".join([
                    f"- {a.type} ({a.severity}): {a.description}" for a in anomalies
                ])
                fallback_context = (
                    "No readable OCR text was extracted from this document. Analyze based on metadata, "
                    "structure, and any available clues.\n\nDetected anomalies summary:\n" + anomalies_summary
                )
                result.gemini_analysis = await self._analyze_with_gemini(fallback_context, filename)
                if isinstance(result.gemini_analysis, dict):
                    result.gemini_analysis.setdefault("note", "OCR text was not available; analysis is based on anomalies/metadata.")

            # Balance sheet specific validation with FMP cross-checks
            try:
                text_for_bs = result.ocr_text or ""
                if text_for_bs and await self._looks_like_balance_sheet(text_for_bs, filename):
                    bs_check = await self._validate_balance_sheet_with_fmp(text_for_bs)
                    # Attach to gemini_analysis payload for frontend display
                    if isinstance(result.gemini_analysis, dict):
                        result.gemini_analysis.setdefault("balance_sheet_check", bs_check)
            except Exception as e:
                # Non-fatal; record error inside gemini_analysis for transparency
                if isinstance(result.gemini_analysis, dict):
                    result.gemini_analysis.setdefault("balance_sheet_check", {"error": str(e)})
            
            # Perform enhanced multi-source validation
            if result.ocr_text and len(result.ocr_text.strip()) > 50:
                try:
                    basic_anomalies = [anomaly.model_dump() for anomaly in anomalies]
                    basic_score = await self._calculate_authenticity_score(result)
                    
                    result.enhanced_validation = await enhanced_document_validator.validate_document(
                        result.ocr_text, filename, basic_anomalies, basic_score
                    )
                    
                    # Use enhanced score if available
                    if result.enhanced_validation:
                        result.score = result.enhanced_validation.overall_authenticity_score
                        result.is_likely_fake = not result.enhanced_validation.is_likely_authentic
                    else:
                        result.score = basic_score
                        result.is_likely_fake = result.score < 40
                        
                except Exception as e:
                    print(f"Enhanced validation failed: {e}")
                    # Fall back to basic scoring
                    result.score = await self._calculate_authenticity_score(result)
                    result.is_likely_fake = result.score < 40
            else:
                # Basic scoring for short or no text
                result.score = await self._calculate_authenticity_score(result)
                result.is_likely_fake = result.score < 40
            
        except Exception as e:
            print(f"Error during PDF analysis: {e}")
            # Add error as anomaly
            result.anomalies.append(PDFAnomalyResult(
                type="processing",
                severity="high",
                description=f"Error during analysis: {str(e)}",
                details={"error_type": type(e).__name__}
            ))
            result.score = 20  # Low score for processing errors
            result.is_likely_fake = True
        
        # Calculate processing time
        result.processing_time_ms = int((time.time() - start_time) * 1000)
        
        return result
    
    async def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of the file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    async def _extract_text_ocr(self, file_path: str) -> str:
        """Extract text using OCR (Tesseract)"""
        if not OCR_AVAILABLE:
            return await self._extract_text_fallback(file_path)
        
        try:
            # Convert PDF to images
            images = convert_from_path(file_path, dpi=250, first_page=1, last_page=10)  # Try up to first 10 pages
            
            extracted_text = []
            for i, image in enumerate(images):
                # Save image temporarily
                temp_image_path = self.temp_dir / f"temp_page_{i}.png"
                image.save(temp_image_path, 'PNG')
                
                try:
                    # Extract text using Tesseract
                    text = pytesseract.image_to_string(image, lang='eng')
                    if text.strip():
                        extracted_text.append(f"--- Page {i+1} ---\n{text}")
                    else:
                        # Grayscale retry for low-contrast scans
                        try:
                            img_gray = image.convert('L')
                            text2 = pytesseract.image_to_string(img_gray, lang='eng')
                            if text2.strip():
                                extracted_text.append(f"--- Page {i+1} (gray) ---\n{text2}")
                        except Exception:
                            pass
                finally:
                    # Clean up temporary image
                    if temp_image_path.exists():
                        temp_image_path.unlink()
            
            # If still empty, try a second pass with higher DPI but fewer pages (safety net)
            if not extracted_text:
                try:
                    images2 = convert_from_path(file_path, dpi=300, first_page=1, last_page=5)
                    for j, image2 in enumerate(images2):
                        text3 = pytesseract.image_to_string(image2, lang='eng')
                        if text3.strip():
                            extracted_text.append(f"--- Page {j+1} (300dpi) ---\n{text3}")
                except Exception:
                    pass

            return "\n\n".join(extracted_text)
            
        except Exception as e:
            print(f"OCR extraction failed: {e}")
            return await self._extract_text_fallback(file_path)
    
    async def _extract_text_fallback(self, file_path: str) -> str:
        """Fallback text extraction using PyPDF2"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = []
                
                # Extract text from first 5 pages
                for page_num in range(min(len(pdf_reader.pages), 5)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text.strip():
                        text_content.append(f"--- Page {page_num+1} ---\n{text}")
                
                return "\n\n".join(text_content)
        except Exception as e:
            print(f"Fallback text extraction failed: {e}")
            return ""
    
    async def _detect_anomalies(self, file_path: str, ocr_text: str) -> List[PDFAnomalyResult]:
        """Detect various anomalies in the PDF"""
        anomalies = []
        
        try:
            # Metadata anomalies
            metadata_anomalies = await self._check_metadata_anomalies(file_path)
            anomalies.extend(metadata_anomalies)
            
            # Content anomalies
            content_anomalies = await self._check_content_anomalies(ocr_text)
            anomalies.extend(content_anomalies)
            
            # Structure anomalies
            structure_anomalies = await self._check_structure_anomalies(file_path)
            anomalies.extend(structure_anomalies)
            
        except Exception as e:
            print(f"Error detecting anomalies: {e}")
            anomalies.append(PDFAnomalyResult(
                type="detection_error",
                severity="medium",
                description=f"Could not complete anomaly detection: {str(e)}"
            ))
        
        return anomalies
    
    async def _check_metadata_anomalies(self, file_path: str) -> List[PDFAnomalyResult]:
        """Check for metadata-related anomalies"""
        anomalies = []
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                metadata = pdf_reader.metadata
                
                if metadata:
                    # Check for suspicious creation/modification dates
                    if '/CreationDate' in metadata and '/ModDate' in metadata:
                        creation_date = str(metadata['/CreationDate'])
                        mod_date = str(metadata['/ModDate'])
                        
                        # Check if modification date is before creation date
                        if creation_date > mod_date:
                            anomalies.append(PDFAnomalyResult(
                                type="metadata",
                                severity="high",
                                description="Modification date is before creation date",
                                details={"creation_date": creation_date, "mod_date": mod_date}
                            ))
                    
                    # Check for suspicious producer/creator
                    producer = str(metadata.get('/Producer', ''))
                    creator = str(metadata.get('/Creator', ''))
                    
                    suspicious_producers = ['fake', 'test', 'demo', 'sample', 'temp']
                    if any(sus in producer.lower() for sus in suspicious_producers):
                        anomalies.append(PDFAnomalyResult(
                            type="metadata",
                            severity="medium",
                            description="Suspicious producer information",
                            details={"producer": producer}
                        ))
                    
                    # Check for missing standard metadata
                    if not metadata.get('/Title') and not metadata.get('/Subject'):
                        anomalies.append(PDFAnomalyResult(
                            type="metadata",
                            severity="low",
                            description="Missing standard document metadata",
                            details={"missing_fields": ["title", "subject"]}
                        ))
                
        except Exception as e:
            print(f"Metadata check failed: {e}")
        
        return anomalies
    
    async def _check_content_anomalies(self, ocr_text: str) -> List[PDFAnomalyResult]:
        """Check for content-related anomalies"""
        anomalies = []
        
        if not ocr_text or len(ocr_text.strip()) < 10:
            anomalies.append(PDFAnomalyResult(
                type="content",
                severity="high",
                description="No readable text content found",
                details={"text_length": len(ocr_text) if ocr_text else 0}
            ))
            return anomalies
        
        text_lower = ocr_text.lower()
        
        # Check for common fake document indicators
        fake_indicators = [
            "sample", "demo", "test document", "placeholder", "lorem ipsum",
            "fake", "not real", "for demonstration", "template"
        ]
        
        found_indicators = [indicator for indicator in fake_indicators if indicator in text_lower]
        if found_indicators:
            anomalies.append(PDFAnomalyResult(
                type="content",
                severity="high",
                description="Contains fake document indicators",
                details={"indicators": found_indicators}
            ))
        
        # Check for SEBI-specific content if claiming to be from SEBI
        if "sebi" in text_lower or "securities and exchange board" in text_lower:
            sebi_indicators = [
                "securities and exchange board of india",
                "sebi act", "regulation", "circular", "notification"
            ]
            
            sebi_score = sum(1 for indicator in sebi_indicators if indicator in text_lower)
            if sebi_score < 2:
                anomalies.append(PDFAnomalyResult(
                    type="content",
                    severity="medium",
                    description="Claims to be SEBI document but lacks authentic SEBI language",
                    details={"sebi_indicators_found": sebi_score}
                ))
        
        # Check for poor OCR quality (too many special characters)
        special_char_ratio = len([c for c in ocr_text if not c.isalnum() and not c.isspace()]) / len(ocr_text)
        if special_char_ratio > 0.3:
            anomalies.append(PDFAnomalyResult(
                type="content",
                severity="medium",
                description="Poor text quality or OCR errors detected",
                details={"special_char_ratio": round(special_char_ratio, 3)}
            ))
        
        return anomalies
    
    async def _check_structure_anomalies(self, file_path: str) -> List[PDFAnomalyResult]:
        """Check for structural anomalies"""
        anomalies = []
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Check for encrypted PDF
                if pdf_reader.is_encrypted:
                    anomalies.append(PDFAnomalyResult(
                        type="structure",
                        severity="medium",
                        description="Document is encrypted",
                        details={"encrypted": True}
                    ))
                
                # Check page count
                page_count = len(pdf_reader.pages)
                if page_count == 0:
                    anomalies.append(PDFAnomalyResult(
                        type="structure",
                        severity="high",
                        description="Document has no pages",
                        details={"page_count": page_count}
                    ))
                elif page_count > 100:
                    anomalies.append(PDFAnomalyResult(
                        type="structure",
                        severity="low",
                        description="Unusually large document",
                        details={"page_count": page_count}
                    ))
                
                # Check for form fields (might indicate template)
                if hasattr(pdf_reader, 'get_form_text_fields'):
                    try:
                        form_fields = pdf_reader.get_form_text_fields()
                        if form_fields:
                            anomalies.append(PDFAnomalyResult(
                                type="structure",
                                severity="medium",
                                description="Document contains form fields",
                                details={"form_fields_count": len(form_fields)}
                            ))
                    except:
                        pass  # Not all PDF versions support this
                
        except Exception as e:
            print(f"Structure check failed: {e}")
        
        return anomalies
    
    async def _analyze_with_gemini(self, text: str, filename: str) -> Dict:
        """Analyze document content with Gemini AI"""
        try:
            # Use the existing Gemini service but with a document analysis approach
            result = await self._gemini_document_analysis(text, filename)
            return result
                
        except Exception as e:
            print(f"Gemini analysis failed: {e}")
            return {
                "authenticity_assessment": "unclear",
                "confidence": 0.0,
                "red_flags": [f"Analysis failed: {str(e)}"],
                "positive_indicators": [],
                "document_type_assessment": "unclear",
                "language_quality": "unclear",
                "recommendations": ["Manual verification required"]
            }
    
    async def _gemini_document_analysis(self, text: str, filename: str) -> Dict:
        """Perform document analysis using Gemini API or mock"""
        if self.gemini_service.use_mock:
            return await self._mock_document_analysis(text, filename)
        
        try:
            prompt = f"""
Analyze this document text for authenticity and legitimacy. The document filename is: {filename}

Consider these factors:
1. Language quality and professionalism
2. Consistency with claimed document type
3. Presence of official terminology and structure
4. Signs of forgery or manipulation
5. Regulatory compliance language

Provide a JSON response with:
{{
    "authenticity_assessment": "authentic|suspicious|likely_fake",
    "confidence": 0.0-1.0,
    "red_flags": ["flag1", "flag2", ...],
    "positive_indicators": ["indicator1", "indicator2", ...],
    "document_type_assessment": "matches_claimed_type|inconsistent|unclear",
    "language_quality": "professional|poor|mixed",
    "recommendations": ["recommendation1", "recommendation2", ...]
}}

Document text (first 2000 characters):
{text[:2000]}
"""
            
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.gemini_service.base_url}/models/gemini-2.0-flash-exp:generateContent",
                    headers={"Content-Type": "application/json"},
                    params={"key": self.gemini_service.api_key},
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {
                            "temperature": 0.1,
                            "maxOutputTokens": 1000,
                        }
                    },
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    raise Exception(f"Gemini API error: {response.status_code}")
                
                result = response.json()
                content = result["candidates"][0]["content"]["parts"][0]["text"]
                
                # Parse JSON response
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    raise Exception("No valid JSON found in response")
                    
        except Exception as e:
            print(f"Gemini API call failed: {e}, using mock analysis")
            return await self._mock_document_analysis(text, filename)
    
    async def _mock_document_analysis(self, text: str, filename: str) -> Dict:
        """Mock document analysis for development/fallback"""
        await asyncio.sleep(0.3)  # Simulate API call
        
        text_lower = text.lower()
        filename_lower = filename.lower()
        
        # Analyze content for authenticity indicators
        fake_indicators = ["sample", "demo", "test", "placeholder", "lorem ipsum", "fake", "not real"]
        sebi_indicators = ["securities and exchange board", "sebi", "regulation", "circular", "notification"]
        professional_indicators = ["pursuant", "hereby", "whereas", "compliance", "regulatory"]
        
        fake_count = sum(1 for indicator in fake_indicators if indicator in text_lower)
        sebi_count = sum(1 for indicator in sebi_indicators if indicator in text_lower)
        professional_count = sum(1 for indicator in professional_indicators if indicator in text_lower)
        
        red_flags = []
        positive_indicators = []
        
        # Determine authenticity assessment
        if fake_count > 0:
            authenticity = "likely_fake"
            confidence = 0.9
            red_flags.extend([f"Contains fake indicators: {fake_indicators[:fake_count]}"])
        elif len(text) < 100:
            authenticity = "suspicious"
            confidence = 0.7
            red_flags.append("Very short document content")
        elif sebi_count > 0 and professional_count > 1:
            authenticity = "authentic"
            confidence = 0.8
            positive_indicators.extend(["Contains SEBI terminology", "Professional language structure"])
        elif professional_count > 0:
            authenticity = "authentic"
            confidence = 0.6
            positive_indicators.append("Professional language detected")
        else:
            authenticity = "suspicious"
            confidence = 0.5
            red_flags.append("Lacks professional regulatory language")
        
        # Check document type consistency
        if "sebi" in filename_lower or "sebi" in text_lower:
            if sebi_count >= 2:
                doc_type_assessment = "matches_claimed_type"
                positive_indicators.append("Consistent with SEBI document format")
            else:
                doc_type_assessment = "inconsistent"
                red_flags.append("Claims to be SEBI document but lacks SEBI terminology")
        else:
            doc_type_assessment = "matches_claimed_type"
        
        # Assess language quality
        if len(text) > 1000 and professional_count > 2:
            language_quality = "professional"
        elif len(text) > 500 and professional_count > 0:
            language_quality = "mixed"
        else:
            language_quality = "poor"
            red_flags.append("Poor language quality or structure")
        
        # Generate recommendations
        recommendations = ["Verify document with official source"]
        if authenticity == "likely_fake":
            recommendations.extend(["Do not trust this document", "Report suspicious document"])
        elif authenticity == "suspicious":
            recommendations.extend(["Exercise caution", "Seek additional verification"])
        else:
            recommendations.append("Document appears legitimate but verify independently")
        
        return {
            "authenticity_assessment": authenticity,
            "confidence": confidence,
            "red_flags": red_flags,
            "positive_indicators": positive_indicators,
            "document_type_assessment": doc_type_assessment,
            "language_quality": language_quality,
            "recommendations": recommendations
        }
    
    async def _calculate_authenticity_score(self, result: PDFAnalysisResult) -> int:
        """Calculate overall authenticity score (0-100)"""
        base_score = 70  # Start with neutral-positive score
        
        # Deduct points for anomalies
        for anomaly in result.anomalies:
            if anomaly.severity == "high":
                base_score -= 25
            elif anomaly.severity == "medium":
                base_score -= 15
            elif anomaly.severity == "low":
                base_score -= 5
        
        # Adjust based on Gemini analysis
        if result.gemini_analysis:
            assessment = result.gemini_analysis.get("authenticity_assessment", "")
            confidence = result.gemini_analysis.get("confidence", 0.5)
            
            if assessment == "likely_fake":
                base_score -= int(30 * confidence)
            elif assessment == "suspicious":
                base_score -= int(15 * confidence)
            elif assessment == "authentic":
                base_score += int(10 * confidence)
        
        # Adjust based on text content quality
        if result.ocr_text:
            text_length = len(result.ocr_text.strip())
            if text_length < 100:
                base_score -= 20  # Very short documents are suspicious
            elif text_length > 2000:
                base_score += 5   # Longer documents are generally more authentic
        else:
            base_score -= 30  # No readable text is very suspicious
        
        # Ensure score is within bounds
        return max(0, min(100, base_score))

# Global service instance
pdf_service = PDFAnalysisService()