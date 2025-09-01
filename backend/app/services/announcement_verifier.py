"""
Corporate Announcement Cross-Verification Service
Verifies announcements against multiple sources and historical data
"""
import asyncio
import aiohttp
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import re
from sqlalchemy.orm import Session
from app.models.announcements import CorporateAnnouncement, AnnouncementVerification, HistoricalPerformance
from app.services.gemini_service import gemini_service
from app.exceptions import ExternalServiceException

logger = logging.getLogger(__name__)

@dataclass
class VerificationResult:
    verification_type: str
    status: str  # verified, disputed, inconclusive
    confidence_score: float  # 0-1
    details: Dict
    discrepancies: List[str]
    source_data: Dict
    cross_reference_url: Optional[str] = None

class CounterpartyVerifier:
    """Verify announcements against counterparty disclosures"""
    
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def verify_merger_acquisition(self, announcement: CorporateAnnouncement) -> VerificationResult:
        """Verify merger/acquisition announcements against counterparty filings"""
        try:
            # Extract counterparty information from announcement
            counterparties = self._extract_counterparties(announcement.content)
            
            if not counterparties:
                return VerificationResult(
                    verification_type="counterparty",
                    status="inconclusive",
                    confidence_score=0.0,
                    details={"reason": "No counterparties identified"},
                    discrepancies=[],
                    source_data={}
                )
            
            verification_results = []
            
            for counterparty in counterparties:
                # Search for counterparty's corresponding announcement
                counterparty_announcement = await self._search_counterparty_announcement(
                    counterparty, announcement.company_symbol, announcement.announcement_date
                )
                
                if counterparty_announcement:
                    # Compare details
                    comparison = await self._compare_announcements(announcement, counterparty_announcement)
                    verification_results.append(comparison)
            
            # Aggregate results
            return self._aggregate_verification_results(verification_results, "counterparty")
            
        except Exception as e:
            logger.error(f"Error in counterparty verification: {str(e)}")
            return VerificationResult(
                verification_type="counterparty",
                status="inconclusive",
                confidence_score=0.0,
                details={"error": str(e)},
                discrepancies=[],
                source_data={}
            )
    
    def _extract_counterparties(self, content: str) -> List[str]:
        """Extract counterparty company names from announcement content"""
        # Common patterns for counterparty mentions
        patterns = [
            r'with\s+([A-Z][A-Za-z\s&]+(?:Ltd|Limited|Inc|Corporation|Corp))',
            r'acquire\s+([A-Z][A-Za-z\s&]+(?:Ltd|Limited|Inc|Corporation|Corp))',
            r'merger\s+with\s+([A-Z][A-Za-z\s&]+(?:Ltd|Limited|Inc|Corporation|Corp))',
            r'joint\s+venture\s+with\s+([A-Z][A-Za-z\s&]+(?:Ltd|Limited|Inc|Corporation|Corp))'
        ]
        
        counterparties = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            counterparties.extend([match.strip() for match in matches])
        
        return list(set(counterparties))  # Remove duplicates
    
    async def _search_counterparty_announcement(self, counterparty: str, original_company: str, date: datetime) -> Optional[Dict]:
        """Search for counterparty's announcement about the same deal"""
        # This would search NSE/BSE announcements for the counterparty
        # For now, we'll simulate this with a basic search
        
        search_window = timedelta(days=7)  # Search within 7 days
        
        # In a real implementation, this would query the announcements database
        # or make API calls to search for counterparty announcements
        
        return None  # Placeholder
    
    async def _compare_announcements(self, original: CorporateAnnouncement, counterparty: Dict) -> Dict:
        """Compare original announcement with counterparty announcement"""
        # Use AI to compare the announcements for consistency
        prompt = f"""
        Compare these two corporate announcements for consistency:
        
        Original Announcement:
        Company: {original.company_name}
        Title: {original.title}
        Content: {original.content}
        
        Counterparty Announcement:
        {counterparty}
        
        Analyze for:
        1. Deal terms consistency
        2. Timeline alignment
        3. Financial figures matching
        4. Any discrepancies
        
        Return a JSON with: consistent (boolean), discrepancies (list), confidence (0-1)
        """
        
        try:
            ai_result = await gemini_service.analyze_with_prompt(prompt)
            return ai_result
        except Exception as e:
            logger.error(f"AI comparison failed: {str(e)}")
            return {"consistent": False, "discrepancies": ["AI analysis failed"], "confidence": 0.0}
    
    def _aggregate_verification_results(self, results: List[Dict], verification_type: str) -> VerificationResult:
        """Aggregate multiple verification results"""
        if not results:
            return VerificationResult(
                verification_type=verification_type,
                status="inconclusive",
                confidence_score=0.0,
                details={"reason": "No verification data available"},
                discrepancies=[],
                source_data={}
            )
        
        # Calculate overall confidence and status
        total_confidence = sum(r.get("confidence", 0) for r in results) / len(results)
        all_discrepancies = []
        
        for result in results:
            all_discrepancies.extend(result.get("discrepancies", []))
        
        if total_confidence > 0.8 and not all_discrepancies:
            status = "verified"
        elif total_confidence < 0.3 or len(all_discrepancies) > 2:
            status = "disputed"
        else:
            status = "inconclusive"
        
        return VerificationResult(
            verification_type=verification_type,
            status=status,
            confidence_score=total_confidence,
            details={"results_count": len(results), "analysis": results},
            discrepancies=all_discrepancies,
            source_data={"verification_results": results}
        )

class HistoricalPerformanceVerifier:
    """Verify announcements against historical company performance"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def verify_performance_claims(self, announcement: CorporateAnnouncement) -> VerificationResult:
        """Verify performance claims against historical data"""
        try:
            # Extract performance claims from announcement
            claims = self._extract_performance_claims(announcement.content)
            
            if not claims:
                return VerificationResult(
                    verification_type="historical_performance",
                    status="inconclusive",
                    confidence_score=0.0,
                    details={"reason": "No performance claims found"},
                    discrepancies=[],
                    source_data={}
                )
            
            # Get historical performance data
            historical_data = self._get_historical_performance(announcement.company_symbol)
            
            if not historical_data:
                return VerificationResult(
                    verification_type="historical_performance",
                    status="inconclusive",
                    confidence_score=0.0,
                    details={"reason": "No historical data available"},
                    discrepancies=[],
                    source_data={}
                )
            
            # Analyze claims against historical trends
            analysis = await self._analyze_performance_consistency(claims, historical_data)
            
            return VerificationResult(
                verification_type="historical_performance",
                status=analysis["status"],
                confidence_score=analysis["confidence"],
                details=analysis["details"],
                discrepancies=analysis["discrepancies"],
                source_data={"historical_data": historical_data, "claims": claims}
            )
            
        except Exception as e:
            logger.error(f"Error in historical performance verification: {str(e)}")
            return VerificationResult(
                verification_type="historical_performance",
                status="inconclusive",
                confidence_score=0.0,
                details={"error": str(e)},
                discrepancies=[],
                source_data={}
            )
    
    def _extract_performance_claims(self, content: str) -> List[Dict]:
        """Extract performance claims from announcement content"""
        claims = []
        
        # Patterns for performance claims
        patterns = {
            'revenue_growth': r'revenue.*?(?:growth|increase|rise).*?(\d+(?:\.\d+)?)\s*%',
            'profit_growth': r'profit.*?(?:growth|increase|rise).*?(\d+(?:\.\d+)?)\s*%',
            'market_share': r'market\s+share.*?(\d+(?:\.\d+)?)\s*%',
            'expansion': r'expand.*?(\d+)\s*(?:stores|locations|branches|offices)',
            'revenue_target': r'revenue.*?(?:target|expect|project).*?(?:Rs\.?\s*)?(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:crore|lakh|million|billion)'
        }
        
        for claim_type, pattern in patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                claims.append({
                    'type': claim_type,
                    'value': match,
                    'context': self._extract_context(content, match)
                })
        
        return claims
    
    def _extract_context(self, content: str, value: str) -> str:
        """Extract context around a value in the content"""
        # Find the sentence containing the value
        sentences = content.split('.')
        for sentence in sentences:
            if value in sentence:
                return sentence.strip()
        return ""
    
    def _get_historical_performance(self, company_symbol: str) -> List[Dict]:
        """Get historical performance data for the company"""
        try:
            # Query last 8 quarters of data
            historical_records = self.db.query(HistoricalPerformance).filter(
                HistoricalPerformance.company_symbol == company_symbol
            ).order_by(HistoricalPerformance.quarter.desc()).limit(8).all()
            
            return [
                {
                    'quarter': record.quarter,
                    'revenue': record.revenue,
                    'profit': record.profit,
                    'growth_rate': record.growth_rate,
                    'market_cap': record.market_cap
                }
                for record in historical_records
            ]
            
        except Exception as e:
            logger.error(f"Error fetching historical data: {str(e)}")
            return []
    
    async def _analyze_performance_consistency(self, claims: List[Dict], historical_data: List[Dict]) -> Dict:
        """Analyze consistency between claims and historical performance"""
        
        prompt = f"""
        Analyze the consistency between these performance claims and historical data:
        
        Performance Claims:
        {claims}
        
        Historical Performance Data (last 8 quarters):
        {historical_data}
        
        Evaluate:
        1. Are the claimed growth rates realistic based on historical trends?
        2. Are there any sudden, unexplained improvements?
        3. Do the claims align with the company's historical performance pattern?
        4. Identify any red flags or inconsistencies
        
        Return JSON with:
        - status: "verified", "disputed", or "inconclusive"
        - confidence: 0-1 score
        - discrepancies: list of specific issues found
        - details: detailed analysis
        """
        
        try:
            analysis = await gemini_service.analyze_with_prompt(prompt)
            return analysis
        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")
            return {
                "status": "inconclusive",
                "confidence": 0.0,
                "discrepancies": ["AI analysis failed"],
                "details": {"error": str(e)}
            }

class PublicDomainVerifier:
    """Verify announcements against public domain information"""
    
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def verify_against_public_sources(self, announcement: CorporateAnnouncement) -> VerificationResult:
        """Verify announcement against public domain sources"""
        try:
            # Search multiple public sources
            sources_to_check = [
                self._check_business_news_sources,
                self._check_regulatory_filings,
                self._check_company_website
            ]
            
            verification_results = []
            
            for source_checker in sources_to_check:
                try:
                    result = await source_checker(announcement)
                    if result:
                        verification_results.append(result)
                except Exception as e:
                    logger.warning(f"Source verification failed: {str(e)}")
                    continue
            
            return self._aggregate_public_domain_results(verification_results)
            
        except Exception as e:
            logger.error(f"Error in public domain verification: {str(e)}")
            return VerificationResult(
                verification_type="public_domain",
                status="inconclusive",
                confidence_score=0.0,
                details={"error": str(e)},
                discrepancies=[],
                source_data={}
            )
    
    async def _check_business_news_sources(self, announcement: CorporateAnnouncement) -> Optional[Dict]:
        """Check business news sources for corroborating information"""
        # Search Economic Times, Business Standard, etc.
        search_terms = [
            f"{announcement.company_name} {announcement.category}",
            f"{announcement.company_symbol} announcement",
            announcement.title[:50]  # First 50 chars of title
        ]
        
        # This would implement actual news source searching
        # For now, return a placeholder
        return {
            "source": "business_news",
            "found_corroboration": False,
            "confidence": 0.5,
            "details": "News source verification not implemented"
        }
    
    async def _check_regulatory_filings(self, announcement: CorporateAnnouncement) -> Optional[Dict]:
        """Check regulatory filings for supporting documentation"""
        # Check SEBI, RBI, MCA filings
        return {
            "source": "regulatory_filings",
            "found_corroboration": False,
            "confidence": 0.5,
            "details": "Regulatory filing verification not implemented"
        }
    
    async def _check_company_website(self, announcement: CorporateAnnouncement) -> Optional[Dict]:
        """Check company's official website for announcement"""
        try:
            # Try to find company website and check for announcement
            # This is a simplified implementation
            return {
                "source": "company_website",
                "found_corroboration": False,
                "confidence": 0.3,
                "details": "Company website verification not implemented"
            }
        except Exception as e:
            logger.warning(f"Company website check failed: {str(e)}")
            return None
    
    def _aggregate_public_domain_results(self, results: List[Dict]) -> VerificationResult:
        """Aggregate public domain verification results"""
        if not results:
            return VerificationResult(
                verification_type="public_domain",
                status="inconclusive",
                confidence_score=0.0,
                details={"reason": "No public domain sources checked successfully"},
                discrepancies=[],
                source_data={}
            )
        
        # Calculate overall confidence
        total_confidence = sum(r.get("confidence", 0) for r in results) / len(results)
        corroborations = sum(1 for r in results if r.get("found_corroboration", False))
        
        if corroborations >= 2:
            status = "verified"
        elif corroborations == 0 and len(results) >= 2:
            status = "disputed"
        else:
            status = "inconclusive"
        
        return VerificationResult(
            verification_type="public_domain",
            status=status,
            confidence_score=total_confidence,
            details={"sources_checked": len(results), "corroborations": corroborations},
            discrepancies=[],
            source_data={"verification_results": results}
        )

class AnnouncementVerificationService:
    """Main service for verifying corporate announcements"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def verify_announcement(self, announcement: CorporateAnnouncement) -> List[VerificationResult]:
        """Perform comprehensive verification of an announcement"""
        verification_results = []
        
        try:
            # Counterparty verification (for M&A announcements)
            if announcement.category in ['merger_acquisition', 'business_agreement']:
                async with CounterpartyVerifier() as verifier:
                    result = await verifier.verify_merger_acquisition(announcement)
                    verification_results.append(result)
            
            # Historical performance verification
            historical_verifier = HistoricalPerformanceVerifier(self.db)
            result = await historical_verifier.verify_performance_claims(announcement)
            verification_results.append(result)
            
            # Public domain verification
            async with PublicDomainVerifier() as verifier:
                result = await verifier.verify_against_public_sources(announcement)
                verification_results.append(result)
            
            # Store verification results in database
            await self._store_verification_results(announcement.id, verification_results)
            
            return verification_results
            
        except Exception as e:
            logger.error(f"Error in announcement verification: {str(e)}")
            return []
    
    async def _store_verification_results(self, announcement_id: str, results: List[VerificationResult]):
        """Store verification results in database"""
        try:
            for result in results:
                verification = AnnouncementVerification(
                    announcement_id=announcement_id,
                    verification_type=result.verification_type,
                    verification_source="automated",
                    status=result.status,
                    confidence_score=result.confidence_score,
                    details=result.details,
                    discrepancies=result.discrepancies,
                    source_data=result.source_data,
                    cross_reference_url=result.cross_reference_url
                )
                
                self.db.add(verification)
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error storing verification results: {str(e)}")
            self.db.rollback()

# Service instance
def get_verification_service(db: Session) -> AnnouncementVerificationService:
    return AnnouncementVerificationService(db)