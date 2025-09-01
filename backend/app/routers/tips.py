from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, validator, Field
from app.database import get_db
from app import crud
from app.services.gemini_service import gemini_service
from app.exceptions import (
    NotFoundException,
    ValidationException,
    ExternalServiceException,
    validate_text_input,
    ErrorDetail
)

router = APIRouter()

class TipCreate(BaseModel):
    message: str = Field(..., min_length=10, max_length=5000, description="Investment tip message")
    source: str = Field(default="manual", pattern="^(manual|api|websocket_test|demo|automated)$", description="Source of the tip")
    submitter_id: Optional[str] = Field(None, max_length=100, description="Optional submitter identifier")
    
    @validator('message')
    def validate_message_content(cls, v):
        from app.exceptions import sanitize_text_input
        if not v or not v.strip():
            raise ValueError('Message cannot be empty')
        
        # Use enhanced sanitization
        try:
            sanitized = sanitize_text_input(v)
            if len(sanitized) < 10:
                raise ValueError('Message too short after sanitization')
            return sanitized
        except Exception as e:
            raise ValueError(f'Message validation failed: {str(e)}')

class TipResponse(BaseModel):
    id: str
    message: str
    source: str
    submitter_id: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=obj.id,
            message=obj.message,
            source=obj.source,
            submitter_id=obj.submitter_id,
            created_at=obj.created_at.isoformat() if obj.created_at else "",
            updated_at=obj.updated_at.isoformat() if obj.updated_at else ""
        )

class CheckTipRequest(BaseModel):
    message: str
    source: str = "manual"
    submitter_id: Optional[str] = None
    
    @validator('message')
    def validate_message(cls, v):
        from app.exceptions import validate_text_input
        # Use enhanced validation and sanitization
        return validate_text_input(v, min_length=10, max_length=5000, field_name="message")
    
    @validator('source')
    def validate_source(cls, v):
        allowed_sources = ['manual', 'api', 'websocket_test', 'demo', 'automated']
        if v not in allowed_sources:
            raise ValueError(f'Source must be one of: {", ".join(allowed_sources)}')
        return v

class RiskAssessmentResponse(BaseModel):
    level: str  # Low, Medium, High
    score: int  # 0-100
    reasons: List[str]
    stock_symbols: List[str]
    advisor: Optional[dict] = None
    timestamp: str
    assessment_id: str
    confidence: float

class CheckTipResponse(BaseModel):
    tip_id: str
    assessment: RiskAssessmentResponse

@router.post("/tips", response_model=TipResponse)
async def create_tip(tip: TipCreate, db: Session = Depends(get_db)):
    """Create a new tip"""
    try:
        # Additional validation
        validate_text_input(tip.message, min_length=10, max_length=5000)
        
        db_tip = crud.create_tip(
            db=db, 
            message=tip.message, 
            source=tip.source, 
            submitter_id=tip.submitter_id
        )
        return db_tip
    except ValidationException:
        raise
    except Exception as e:
        raise ExternalServiceException("database", f"Failed to create tip: {str(e)}")

@router.get("/tips/{tip_id}", response_model=TipResponse)
async def get_tip(tip_id: str, db: Session = Depends(get_db)):
    """Get a specific tip by ID"""
    try:
        # Validate UUID format
        import uuid
        uuid.UUID(tip_id)
    except ValueError:
        raise ValidationException(
            "Invalid tip ID format",
            details=[ErrorDetail(
                code="invalid_uuid",
                message="Tip ID must be a valid UUID",
                field="tip_id"
            )]
        )
    
    db_tip = crud.get_tip(db=db, tip_id=tip_id)
    if db_tip is None:
        raise NotFoundException("Tip", tip_id)
    return db_tip

@router.get("/tips", response_model=List[TipResponse])
async def get_tips(
    skip: int = Query(default=0, ge=0, le=10000, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """Get all tips with pagination"""
    try:
        tips = crud.get_tips(db=db, skip=skip, limit=limit)
        return tips
    except Exception as e:
        raise ExternalServiceException("database", f"Failed to retrieve tips: {str(e)}")

@router.delete("/tips/{tip_id}")
async def delete_tip(tip_id: str, db: Session = Depends(get_db)):
    """Delete a tip"""
    try:
        # Validate UUID format
        import uuid
        uuid.UUID(tip_id)
    except ValueError:
        raise ValidationException(
            "Invalid tip ID format",
            details=[ErrorDetail(
                code="invalid_uuid",
                message="Tip ID must be a valid UUID",
                field="tip_id"
            )]
        )
    
    try:
        success = crud.delete_tip(db=db, tip_id=tip_id)
        if not success:
            raise NotFoundException("Tip", tip_id)
        return {"message": "Tip deleted successfully"}
    except NotFoundException:
        raise
    except Exception as e:
        raise ExternalServiceException("database", f"Failed to delete tip: {str(e)}")

@router.post("/check-tip", response_model=CheckTipResponse)
async def check_tip(request: CheckTipRequest, db: Session = Depends(get_db)):
    """
    Analyze investment tip for risk assessment
    
    This endpoint combines tip creation and risk assessment in a single call.
    It uses Gemini 2.0 Flash API for analysis with fallback to mock analysis.
    
    Requirements: 1.1, 1.2, 1.3, 1.4
    """
    try:
        # Create tip in database
        db_tip = crud.create_tip(
            db=db,
            message=request.message,
            source=request.source,
            submitter_id=request.submitter_id
        )
        
        # Analyze tip using Gemini service
        analysis_result = await gemini_service.analyze_tip(request.message)
        
        # Prepare advisor info if mentioned
        advisor_info = None
        if analysis_result.advisor_mentioned:
            advisor_info = {
                "name": analysis_result.advisor_mentioned,
                "verified": False,  # Will be enhanced in future tasks
                "registration_status": "unknown"
            }
        
        # Create assessment in database
        db_assessment = crud.create_assessment(
            db=db,
            tip_id=db_tip.id,
            level=analysis_result.level,
            score=analysis_result.score,
            reasons=analysis_result.reasons,
            stock_symbols=analysis_result.stock_symbols,
            advisor_info=advisor_info,
            gemini_raw=None,  # Could store raw Gemini response if needed
            confidence=int(analysis_result.confidence * 100)
        )
        
        # Trigger real-time alert for high-risk tips
        if analysis_result.score >= 70:  # High or medium-high risk
            from app.routers.websockets import broadcast_alert, create_high_risk_tip_alert
            
            # Determine sector from stock symbols if available
            sector = None
            if analysis_result.stock_symbols:
                # Simple sector mapping - could be enhanced with real sector lookup
                sector = "Technology"  # Default for demo
            
            alert = create_high_risk_tip_alert(
                tip_id=db_tip.id,
                risk_score=analysis_result.score,
                sector=sector
            )
            
            # Broadcast alert asynchronously (fire and forget)
            try:
                await broadcast_alert(alert)
            except Exception as alert_error:
                # Don't fail the main request if alert fails
                print(f"Failed to broadcast alert: {alert_error}")
        
        # Build response
        assessment_response = RiskAssessmentResponse(
            level=db_assessment.level,
            score=db_assessment.score,
            reasons=db_assessment.reasons,
            stock_symbols=db_assessment.stock_symbols,
            advisor=advisor_info,
            timestamp=db_assessment.created_at.isoformat(),
            assessment_id=db_assessment.id,
            confidence=analysis_result.confidence
        )
        
        return CheckTipResponse(
            tip_id=db_tip.id,
            assessment=assessment_response
        )
        
    except ValidationException:
        raise
    except ExternalServiceException:
        raise
    except Exception as e:
        # Log error and return appropriate HTTP error
        print(f"Error in check_tip: {str(e)}")
        raise ExternalServiceException("gemini_api", f"Failed to analyze tip: {str(e)}")