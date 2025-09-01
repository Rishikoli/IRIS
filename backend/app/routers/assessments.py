from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.database import get_db
from app import crud

router = APIRouter()

class AssessmentCreate(BaseModel):
    tip_id: str
    level: str  # Low, Medium, High
    score: int  # 0-100
    reasons: List[str]
    stock_symbols: List[str] = []
    advisor_info: Optional[dict] = None
    gemini_raw: Optional[dict] = None
    confidence: Optional[int] = None

class AssessmentResponse(BaseModel):
    id: str
    tip_id: str
    level: str
    score: int
    reasons: List[str]
    stock_symbols: List[str]
    advisor_info: Optional[dict]
    confidence: Optional[int]
    created_at: str

    class Config:
        from_attributes = True

@router.post("/assessments", response_model=AssessmentResponse)
async def create_assessment(assessment: AssessmentCreate, db: Session = Depends(get_db)):
    """Create a new assessment"""
    # Verify tip exists
    tip = crud.get_tip(db=db, tip_id=assessment.tip_id)
    if not tip:
        raise HTTPException(status_code=404, detail="Tip not found")
    
    db_assessment = crud.create_assessment(
        db=db,
        tip_id=assessment.tip_id,
        level=assessment.level,
        score=assessment.score,
        reasons=assessment.reasons,
        stock_symbols=assessment.stock_symbols,
        advisor_info=assessment.advisor_info,
        gemini_raw=assessment.gemini_raw,
        confidence=assessment.confidence
    )
    return db_assessment

@router.get("/assessments/{assessment_id}", response_model=AssessmentResponse)
async def get_assessment(assessment_id: str, db: Session = Depends(get_db)):
    """Get a specific assessment by ID"""
    db_assessment = crud.get_assessment(db=db, assessment_id=assessment_id)
    if db_assessment is None:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return db_assessment

@router.get("/assessments", response_model=List[AssessmentResponse])
async def get_assessments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all assessments with pagination"""
    assessments = crud.get_assessments(db=db, skip=skip, limit=limit)
    return assessments

@router.get("/tips/{tip_id}/assessments", response_model=List[AssessmentResponse])
async def get_assessments_by_tip(tip_id: str, db: Session = Depends(get_db)):
    """Get all assessments for a specific tip"""
    # Verify tip exists
    tip = crud.get_tip(db=db, tip_id=tip_id)
    if not tip:
        raise HTTPException(status_code=404, detail="Tip not found")
    
    assessments = crud.get_assessments_by_tip(db=db, tip_id=tip_id)
    return assessments