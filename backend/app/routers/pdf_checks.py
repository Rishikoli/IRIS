from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
import tempfile
import os
from pathlib import Path
from app.database import get_db
from app import crud
from app.services.pdf_service import pdf_service, PDFAnalysisResult
from app.exceptions import (
    ValidationException,
    FileProcessingException,
    ExternalServiceException,
    NotFoundException,
    ErrorDetail,
    validate_file_type,
    validate_file_size
)

router = APIRouter()

class PDFCheckCreate(BaseModel):
    file_hash: str = Field(..., min_length=32, max_length=128, description="File hash (MD5, SHA256, etc.)")
    filename: str = Field(..., min_length=1, max_length=255, description="Original filename")
    file_size: Optional[int] = Field(None, ge=0, le=10485760, description="File size in bytes (max 10MB)")
    ocr_text: Optional[str] = Field(None, max_length=100000, description="Extracted OCR text")
    anomalies: List[dict] = Field(default=[], description="List of detected anomalies")
    score: Optional[int] = Field(None, ge=0, le=100, description="Authenticity score (0-100)")
    is_likely_fake: Optional[bool] = Field(None, description="Whether document is likely fake")
    processing_time_ms: Optional[int] = Field(None, ge=0, description="Processing time in milliseconds")

class PDFCheckResponse(BaseModel):
    id: str
    file_hash: str
    filename: str
    file_size: Optional[int]
    ocr_text: Optional[str]
    anomalies: List[dict]
    score: Optional[int]
    is_likely_fake: Optional[bool]
    processing_time_ms: Optional[int]
    created_at: str

    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=obj.id,
            file_hash=obj.file_hash,
            filename=obj.filename,
            file_size=obj.file_size,
            ocr_text=obj.ocr_text,
            anomalies=obj.anomalies,
            score=obj.score,
            is_likely_fake=obj.is_likely_fake,
            processing_time_ms=obj.processing_time_ms,
            created_at=obj.created_at.isoformat() if obj.created_at else ""
        )

class PDFAnalysisResponse(BaseModel):
    """Response model for PDF analysis endpoint"""
    id: str
    file_hash: str
    filename: str
    file_size: int
    ocr_text: Optional[str]
    anomalies: List[dict]
    score: int  # 0-100 authenticity score
    is_likely_fake: bool
    processing_time_ms: int
    gemini_analysis: Optional[dict]
    enhanced_validation: Optional[dict] = None  # Multi-source validation results
    created_at: str
    
    class Config:
        from_attributes = True

@router.post("/check-pdf", response_model=PDFAnalysisResponse)
async def analyze_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Analyze uploaded PDF for authenticity and detect anomalies.
    
    This endpoint:
    - Accepts PDF file uploads with enhanced security validation
    - Performs OCR text extraction
    - Detects document anomalies using heuristics
    - Analyzes content with Gemini AI
    - Returns authenticity score and detailed analysis
    
    Security features:
    - File type validation with double extension checks
    - File size limits (10MB max)
    - Filename sanitization and security checks
    - Content type validation
    """
    # Enhanced file validation
    if not file.filename:
        raise ValidationException(
            "Filename is required",
            details=[ErrorDetail(
                code="missing_filename",
                message="Uploaded file must have a filename",
                field="filename"
            )]
        )
    
    # Validate content type
    from app.exceptions import validate_content_type
    if file.content_type:
        validate_content_type(file.content_type, ['application/pdf'])
    
    # Validate file type with enhanced security checks
    validate_file_type(file.filename, ['pdf'])
    
    # Read file content for validation
    file_content = await file.read()
    
    # Enhanced file size validation
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MIN_FILE_SIZE = 1024  # 1KB minimum
    
    if len(file_content) < MIN_FILE_SIZE:
        raise ValidationException(
            "File too small to be a valid PDF",
            details=[ErrorDetail(
                code="file_too_small",
                message=f"File size {len(file_content)} bytes is too small for a PDF document",
                field="file_size",
                details={"min_size_bytes": MIN_FILE_SIZE, "current_size": len(file_content)}
            )]
        )
    
    validate_file_size(len(file_content), MAX_FILE_SIZE)
    
    # Validate PDF file signature (magic bytes)
    if not file_content.startswith(b'%PDF-'):
        raise ValidationException(
            "Invalid PDF file format",
            details=[ErrorDetail(
                code="invalid_pdf_signature",
                message="File does not appear to be a valid PDF document",
                field="file_content",
                details={"expected_signature": "%PDF-", "file_start": file_content[:10].hex()}
            )]
        )
    
    # Reset file pointer
    await file.seek(0)
    
    # Create temporary file for processing
    temp_dir = Path(tempfile.gettempdir()) / "iris_pdf_uploads"
    temp_dir.mkdir(exist_ok=True)
    
    temp_file_path = temp_dir / f"upload_{file.filename}"
    
    try:
        # Save uploaded file temporarily
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(file_content)
        
        # Check if this file was already processed (by hash)
        analysis_result = await pdf_service.analyze_pdf(str(temp_file_path), file.filename)
        
        existing = crud.get_pdf_check_by_hash(db=db, file_hash=analysis_result.file_hash)
        if existing:
            # Return existing analysis
            return PDFAnalysisResponse(
                id=existing.id,
                file_hash=existing.file_hash,
                filename=existing.filename,
                file_size=existing.file_size or 0,
                ocr_text=existing.ocr_text,
                anomalies=existing.anomalies,
                score=existing.score or 0,
                is_likely_fake=existing.is_likely_fake or False,
                processing_time_ms=existing.processing_time_ms or 0,
                gemini_analysis=analysis_result.gemini_analysis,
                enhanced_validation=analysis_result.enhanced_validation.model_dump() if analysis_result.enhanced_validation else None,
                created_at=existing.created_at.isoformat()
            )
        
        # Store new analysis in database
        db_pdf_check = crud.create_pdf_check(
            db=db,
            file_hash=analysis_result.file_hash,
            filename=analysis_result.filename,
            file_size=analysis_result.file_size,
            ocr_text=analysis_result.ocr_text,
            anomalies=[anomaly.model_dump() for anomaly in analysis_result.anomalies],
            score=analysis_result.score,
            is_likely_fake=analysis_result.is_likely_fake,
            processing_time_ms=analysis_result.processing_time_ms
        )
        
        # Trigger real-time alert for suspicious documents
        if analysis_result.is_likely_fake or len(analysis_result.anomalies) >= 3:
            from app.routers.websockets import broadcast_alert, create_document_anomaly_alert
            
            alert = create_document_anomaly_alert(
                pdf_id=db_pdf_check.id,
                anomaly_count=len(analysis_result.anomalies),
                filename=analysis_result.filename
            )
            
            # Broadcast alert asynchronously (fire and forget)
            try:
                await broadcast_alert(alert)
            except Exception as alert_error:
                # Don't fail the main request if alert fails
                print(f"Failed to broadcast PDF alert: {alert_error}")
        
        return PDFAnalysisResponse(
            id=db_pdf_check.id,
            file_hash=db_pdf_check.file_hash,
            filename=db_pdf_check.filename,
            file_size=db_pdf_check.file_size or 0,
            ocr_text=db_pdf_check.ocr_text,
            anomalies=db_pdf_check.anomalies,
            score=db_pdf_check.score or 0,
            is_likely_fake=db_pdf_check.is_likely_fake or False,
            processing_time_ms=db_pdf_check.processing_time_ms or 0,
            gemini_analysis=analysis_result.gemini_analysis,
            enhanced_validation=analysis_result.enhanced_validation.model_dump() if analysis_result.enhanced_validation else None,
            created_at=db_pdf_check.created_at.isoformat()
        )
        
    except ValidationException:
        raise
    except FileProcessingException:
        raise
    except Exception as e:
        raise FileProcessingException(f"Error processing PDF: {str(e)}")
    finally:
        # Clean up temporary file
        if temp_file_path.exists():
            temp_file_path.unlink()

@router.post("/pdf-checks", response_model=PDFCheckResponse)
async def create_pdf_check(pdf_check: PDFCheckCreate, db: Session = Depends(get_db)):
    """Create a new PDF check (legacy endpoint)"""
    # Check if file hash already exists
    existing = crud.get_pdf_check_by_hash(db=db, file_hash=pdf_check.file_hash)
    if existing:
        raise HTTPException(status_code=409, detail="PDF with this hash already processed")
    
    db_pdf_check = crud.create_pdf_check(
        db=db,
        file_hash=pdf_check.file_hash,
        filename=pdf_check.filename,
        file_size=pdf_check.file_size,
        ocr_text=pdf_check.ocr_text,
        anomalies=pdf_check.anomalies,
        score=pdf_check.score,
        is_likely_fake=pdf_check.is_likely_fake,
        processing_time_ms=pdf_check.processing_time_ms
    )
    return db_pdf_check

@router.get("/pdf-checks/{pdf_check_id}", response_model=PDFCheckResponse)
async def get_pdf_check(pdf_check_id: str, db: Session = Depends(get_db)):
    """Get a specific PDF check by ID"""
    try:
        # Validate UUID format
        import uuid
        uuid.UUID(pdf_check_id)
    except ValueError:
        raise ValidationException(
            "Invalid PDF check ID format",
            details=[ErrorDetail(
                code="invalid_uuid",
                message="PDF check ID must be a valid UUID",
                field="pdf_check_id"
            )]
        )
    
    try:
        db_pdf_check = crud.get_pdf_check(db=db, pdf_check_id=pdf_check_id)
        if db_pdf_check is None:
            raise NotFoundException("PDF check", pdf_check_id)
        return db_pdf_check
    except NotFoundException:
        raise
    except Exception as e:
        raise ExternalServiceException("database", f"Failed to retrieve PDF check: {str(e)}")

@router.get("/pdf-checks")
async def get_pdf_checks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all PDF checks with pagination"""
    pdf_checks = crud.get_pdf_checks(db=db, skip=skip, limit=limit)
    return [
        {
            "id": check.id,
            "file_hash": check.file_hash,
            "filename": check.filename,
            "file_size": check.file_size,
            "score": check.score,
            "is_likely_fake": check.is_likely_fake,
            "processing_time_ms": check.processing_time_ms,
            "created_at": check.created_at.isoformat() if check.created_at else ""
        }
        for check in pdf_checks
    ]

@router.get("/pdf-checks/hash/{file_hash}", response_model=PDFCheckResponse)
async def get_pdf_check_by_hash(file_hash: str, db: Session = Depends(get_db)):
    """Get PDF check by file hash"""
    db_pdf_check = crud.get_pdf_check_by_hash(db=db, file_hash=file_hash)
    if db_pdf_check is None:
        raise HTTPException(status_code=404, detail="PDF check not found")
    return db_pdf_check