from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.services.advisor_service import AdvisorVerificationService, AdvisorInfo

router = APIRouter()

# Initialize advisor service
advisor_service = AdvisorVerificationService()

class AdvisorSearchResponse(BaseModel):
    """Response model for advisor search"""
    id: str
    name: str
    registration_number: str
    status: str
    registration_date: str
    validity_date: str
    category: str
    contact_info: Optional[Dict[str, Any]] = None
    compliance_score: Optional[int] = None
    match_score: float = Field(..., description="Match score between 0.0 and 1.0")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "ADV001",
                "name": "Rajesh Kumar Sharma",
                "registration_number": "INA000001234",
                "status": "active",
                "registration_date": "2020-01-15",
                "validity_date": "2025-01-14",
                "category": "Investment Adviser",
                "contact_info": {
                    "email": "rajesh.sharma@example.com",
                    "phone": "+91-9876543210",
                    "address": "Mumbai, Maharashtra"
                },
                "compliance_score": 95,
                "match_score": 0.95
            }
        }

class AdvisorSearchRequest(BaseModel):
    """Request model for advisor search"""
    query: str = Field(..., min_length=2, max_length=200, description="Advisor name or registration number")
    limit: Optional[int] = Field(10, ge=1, le=50, description="Maximum number of results")
    min_score: Optional[float] = Field(0.3, ge=0.0, le=1.0, description="Minimum match score threshold")

class AdvisorVerificationResponse(BaseModel):
    """Response model for advisor verification"""
    success: bool
    query: str
    total_matches: int
    advisors: List[AdvisorSearchResponse]
    message: Optional[str] = None
    cache_info: Optional[Dict[str, Any]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "query": "Rajesh Kumar",
                "total_matches": 1,
                "advisors": [
                    {
                        "id": "ADV001",
                        "name": "Rajesh Kumar Sharma",
                        "registration_number": "INA000001234",
                        "status": "active",
                        "registration_date": "2020-01-15",
                        "validity_date": "2025-01-14",
                        "category": "Investment Adviser",
                        "compliance_score": 95,
                        "match_score": 0.95
                    }
                ],
                "message": "Found 1 matching advisor"
            }
        }

class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    error: str
    details: Optional[str] = None

@router.get(
    "/verify-advisor",
    response_model=AdvisorVerificationResponse,
    summary="Verify Financial Advisor",
    description="Search and verify financial advisors in SEBI directory by name or registration number"
)
async def verify_advisor(
    query: str = Query(
        ..., 
        min_length=2, 
        max_length=200,
        description="Advisor name or registration number to search for",
        example="Rajesh Kumar"
    ),
    limit: int = Query(
        10, 
        ge=1, 
        le=50,
        description="Maximum number of results to return"
    ),
    min_score: float = Query(
        0.3,
        ge=0.0,
        le=1.0,
        description="Minimum match score threshold (0.0 to 1.0)"
    ),
    include_cache_info: bool = Query(
        False,
        description="Include cache information in response"
    )
):
    """
    Verify financial advisor registration status with SEBI directory.
    
    This endpoint searches for financial advisors by name or registration number
    and returns their registration status, validity, and other relevant information.
    
    **Query Parameters:**
    - **query**: Advisor name or registration number (minimum 2 characters)
    - **limit**: Maximum results to return (1-50, default: 10)
    - **min_score**: Minimum match confidence (0.0-1.0, default: 0.3)
    - **include_cache_info**: Include cache statistics in response
    
    **Response includes:**
    - Registration status (active/suspended/cancelled)
    - Registration and validity dates
    - Category (Investment Adviser, Research Analyst, etc.)
    - Compliance score (if available)
    - Match confidence score
    
    **Status Meanings:**
    - **active**: Currently registered and authorized
    - **suspended**: Temporarily suspended by SEBI
    - **cancelled**: Registration cancelled/revoked
    """
    try:
        # Validate query
        if not query or len(query.strip()) < 2:
            raise HTTPException(
                status_code=400,
                detail="Query must be at least 2 characters long"
            )
        
        # Search for advisors
        matches = await advisor_service.search_advisors(
            query=query.strip(),
            limit=limit,
            min_score=min_score
        )
        
        # Convert to response format
        advisor_responses = []
        for match in matches:
            advisor = match["advisor"]
            advisor_response = AdvisorSearchResponse(
                id=advisor.id,
                name=advisor.name,
                registration_number=advisor.registration_number,
                status=advisor.status,
                registration_date=advisor.registration_date,
                validity_date=advisor.validity_date,
                category=advisor.category,
                contact_info=advisor.contact_info,
                compliance_score=advisor.compliance_score,
                match_score=round(match["match_score"], 3)
            )
            advisor_responses.append(advisor_response)
        
        # Prepare response message
        if len(advisor_responses) == 0:
            message = f"No advisors found matching '{query}'. Please verify the name or registration number."
        elif len(advisor_responses) == 1:
            message = f"Found 1 matching advisor for '{query}'"
        else:
            message = f"Found {len(advisor_responses)} matching advisors for '{query}'"
        
        # Prepare response
        response_data = {
            "success": True,
            "query": query,
            "total_matches": len(advisor_responses),
            "advisors": advisor_responses,
            "message": message
        }
        
        # Include cache info if requested
        if include_cache_info:
            response_data["cache_info"] = advisor_service.get_cache_stats()
        
        return AdvisorVerificationResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during advisor verification: {str(e)}"
        )

@router.get(
    "/advisor/{advisor_id}",
    response_model=AdvisorSearchResponse,
    summary="Get Advisor by ID",
    description="Get detailed information about a specific advisor by their ID"
)
async def get_advisor_by_id(advisor_id: str):
    """
    Get detailed information about a specific advisor by their ID.
    
    **Path Parameters:**
    - **advisor_id**: Unique advisor identifier
    
    **Returns:**
    - Complete advisor information including contact details and compliance score
    """
    try:
        advisor = await advisor_service.get_advisor_by_id(advisor_id)
        
        if not advisor:
            raise HTTPException(
                status_code=404,
                detail=f"Advisor with ID '{advisor_id}' not found"
            )
        
        return AdvisorSearchResponse(
            id=advisor.id,
            name=advisor.name,
            registration_number=advisor.registration_number,
            status=advisor.status,
            registration_date=advisor.registration_date,
            validity_date=advisor.validity_date,
            category=advisor.category,
            contact_info=advisor.contact_info,
            compliance_score=advisor.compliance_score,
            match_score=1.0  # Perfect match for direct ID lookup
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get(
    "/advisor/registration/{reg_number}",
    response_model=AdvisorSearchResponse,
    summary="Get Advisor by Registration Number",
    description="Get advisor information by their SEBI registration number"
)
async def get_advisor_by_registration(reg_number: str):
    """
    Get advisor information by their SEBI registration number.
    
    **Path Parameters:**
    - **reg_number**: SEBI registration number (e.g., INA000001234)
    
    **Returns:**
    - Complete advisor information if registration number exists
    """
    try:
        advisor = await advisor_service.get_advisor_by_registration_number(reg_number)
        
        if not advisor:
            raise HTTPException(
                status_code=404,
                detail=f"No advisor found with registration number '{reg_number}'"
            )
        
        return AdvisorSearchResponse(
            id=advisor.id,
            name=advisor.name,
            registration_number=advisor.registration_number,
            status=advisor.status,
            registration_date=advisor.registration_date,
            validity_date=advisor.validity_date,
            category=advisor.category,
            contact_info=advisor.contact_info,
            compliance_score=advisor.compliance_score,
            match_score=1.0  # Perfect match for exact registration number
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get(
    "/advisor-cache-stats",
    summary="Get Cache Statistics",
    description="Get advisor cache statistics for monitoring purposes"
)
async def get_cache_stats():
    """
    Get advisor cache statistics for monitoring and debugging.
    
    **Returns:**
    - Cache validity status
    - Cache timestamp
    - Total number of cached advisors
    - Cache TTL configuration
    """
    try:
        return advisor_service.get_cache_stats()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving cache stats: {str(e)}"
        )