from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import re
from dataclasses import dataclass

@dataclass
class AdvisorInfo:
    """Data class for advisor information"""
    id: str
    name: str
    registration_number: str
    status: str  # 'active', 'suspended', 'cancelled'
    registration_date: str
    validity_date: str
    category: str  # 'Investment Adviser', 'Research Analyst', etc.
    contact_info: Optional[Dict[str, Any]] = None
    compliance_score: Optional[int] = None

class AdvisorVerificationService:
    """Service for verifying financial advisors against SEBI directory"""
    
    def __init__(self):
        # In-memory cache for advisor data
        self._cache: Dict[str, List[AdvisorInfo]] = {}
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl = timedelta(hours=24)  # Cache for 24 hours
        
        # Initialize with sample SEBI data
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize with sample SEBI advisor data for demo purposes"""
        sample_advisors = [
            AdvisorInfo(
                id="ADV001",
                name="Rajesh Kumar Sharma",
                registration_number="INA000001234",
                status="active",
                registration_date="2020-01-15",
                validity_date="2025-01-14",
                category="Investment Adviser",
                contact_info={
                    "email": "rajesh.sharma@example.com",
                    "phone": "+91-9876543210",
                    "address": "Mumbai, Maharashtra"
                },
                compliance_score=95
            ),
            AdvisorInfo(
                id="ADV002",
                name="Priya Patel",
                registration_number="INA000002345",
                status="active",
                registration_date="2019-06-20",
                validity_date="2024-06-19",
                category="Research Analyst",
                contact_info={
                    "email": "priya.patel@example.com",
                    "phone": "+91-9876543211",
                    "address": "Ahmedabad, Gujarat"
                },
                compliance_score=88
            ),
            AdvisorInfo(
                id="ADV003",
                name="Amit Singh",
                registration_number="INA000003456",
                status="suspended",
                registration_date="2018-03-10",
                validity_date="2023-03-09",
                category="Investment Adviser",
                contact_info={
                    "email": "amit.singh@example.com",
                    "phone": "+91-9876543212",
                    "address": "Delhi, NCR"
                },
                compliance_score=45
            ),
            AdvisorInfo(
                id="ADV004",
                name="Sunita Agarwal",
                registration_number="INA000004567",
                status="active",
                registration_date="2021-09-05",
                validity_date="2026-09-04",
                category="Portfolio Manager",
                contact_info={
                    "email": "sunita.agarwal@example.com",
                    "phone": "+91-9876543213",
                    "address": "Bangalore, Karnataka"
                },
                compliance_score=92
            ),
            AdvisorInfo(
                id="ADV005",
                name="Vikram Gupta",
                registration_number="INA000005678",
                status="cancelled",
                registration_date="2017-12-01",
                validity_date="2022-11-30",
                category="Investment Adviser",
                contact_info={
                    "email": "vikram.gupta@example.com",
                    "phone": "+91-9876543214",
                    "address": "Pune, Maharashtra"
                },
                compliance_score=25
            ),
            AdvisorInfo(
                id="ADV006",
                name="Dr. Meera Krishnan",
                registration_number="INA000006789",
                status="active",
                registration_date="2020-07-15",
                validity_date="2025-07-14",
                category="Research Analyst",
                contact_info={
                    "email": "meera.krishnan@example.com",
                    "phone": "+91-9876543215",
                    "address": "Chennai, Tamil Nadu"
                },
                compliance_score=96
            )
        ]
        
        # Cache the sample data
        self._cache["all_advisors"] = sample_advisors
        self._cache_timestamp = datetime.utcnow()
    
    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid"""
        if not self._cache_timestamp:
            return False
        return datetime.utcnow() - self._cache_timestamp < self._cache_ttl
    
    def _normalize_query(self, query: str) -> str:
        """Normalize search query for better matching"""
        # Remove extra spaces, convert to lowercase
        normalized = re.sub(r'\s+', ' ', query.strip().lower())
        return normalized
    
    def _calculate_match_score(self, advisor: AdvisorInfo, query: str) -> float:
        """Calculate match score between advisor and query"""
        query_normalized = self._normalize_query(query)
        name_normalized = self._normalize_query(advisor.name)
        reg_num_normalized = advisor.registration_number.lower()
        
        score = 0.0
        
        # Exact registration number match gets highest score
        if query_normalized == reg_num_normalized:
            return 1.0
        
        # Partial registration number match
        if query_normalized in reg_num_normalized or reg_num_normalized in query_normalized:
            score += 0.8
        
        # Name matching
        query_words = query_normalized.split()
        name_words = name_normalized.split()
        
        # Exact name match
        if query_normalized == name_normalized:
            score += 0.9
        else:
            # Partial name matching
            matching_words = 0
            for query_word in query_words:
                for name_word in name_words:
                    if query_word in name_word or name_word in query_word:
                        matching_words += 1
                        break
            
            if len(query_words) > 0:
                word_match_ratio = matching_words / len(query_words)
                score += word_match_ratio * 0.7
        
        return min(score, 1.0)
    
    async def search_advisors(
        self, 
        query: str, 
        limit: int = 10,
        min_score: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Search for advisors by name or registration number
        
        Args:
            query: Search query (name or registration number)
            limit: Maximum number of results to return
            min_score: Minimum match score threshold
            
        Returns:
            List of matching advisors with match scores
        """
        if not query or len(query.strip()) < 2:
            return []
        
        # Ensure cache is valid
        if not self._is_cache_valid():
            self._initialize_sample_data()
        
        all_advisors = self._cache.get("all_advisors", [])
        matches = []
        
        for advisor in all_advisors:
            match_score = self._calculate_match_score(advisor, query)
            
            if match_score >= min_score:
                matches.append({
                    "advisor": advisor,
                    "match_score": match_score
                })
        
        # Sort by match score (descending) and compliance score (descending)
        matches.sort(key=lambda x: (x["match_score"], x["advisor"].compliance_score or 0), reverse=True)
        
        # Return top matches
        return matches[:limit]
    
    async def get_advisor_by_id(self, advisor_id: str) -> Optional[AdvisorInfo]:
        """Get advisor by ID"""
        if not self._is_cache_valid():
            self._initialize_sample_data()
        
        all_advisors = self._cache.get("all_advisors", [])
        for advisor in all_advisors:
            if advisor.id == advisor_id:
                return advisor
        
        return None
    
    async def get_advisor_by_registration_number(self, reg_number: str) -> Optional[AdvisorInfo]:
        """Get advisor by registration number"""
        if not self._is_cache_valid():
            self._initialize_sample_data()
        
        all_advisors = self._cache.get("all_advisors", [])
        for advisor in all_advisors:
            if advisor.registration_number.lower() == reg_number.lower():
                return advisor
        
        return None
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for monitoring"""
        return {
            "cache_valid": self._is_cache_valid(),
            "cache_timestamp": self._cache_timestamp.isoformat() if self._cache_timestamp else None,
            "total_advisors": len(self._cache.get("all_advisors", [])),
            "cache_ttl_hours": self._cache_ttl.total_seconds() / 3600
        }