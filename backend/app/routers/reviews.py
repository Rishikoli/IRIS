from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, field_serializer
from datetime import datetime
from app.database import get_db
from app import crud

router = APIRouter()

class ReviewCreate(BaseModel):
    case_id: str
    case_type: str  # 'assessment', 'pdf_check', 'fraud_chain'
    reviewer_id: str
    ai_decision: dict
    decision: str  # 'approve', 'override', 'needs_more_info'
    notes: Optional[str] = None
    human_decision: Optional[dict] = None
    ai_confidence: Optional[int] = None
    priority: str = "medium"  # 'low', 'medium', 'high'

class ReviewDecision(BaseModel):
    decision: str  # 'approve', 'override', 'needs_more_info'
    notes: Optional[str] = None
    human_decision: Optional[dict] = None

class ReviewResponse(BaseModel):
    id: str
    case_id: str
    case_type: str
    reviewer_id: str
    ai_decision: dict
    human_decision: Optional[dict]
    decision: str
    notes: Optional[str]
    ai_confidence: Optional[int]
    priority: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        
    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat() if dt else ""

class QueueItemResponse(BaseModel):
    review_id: str
    case_id: str
    case_type: str
    priority: str
    ai_confidence: Optional[int]
    ai_decision: dict
    created_at: str
    case_details: dict

class ReviewStatisticsResponse(BaseModel):
    total_reviews: int
    pending_reviews: int
    completed_reviews: int
    pending_by_priority: dict
    reviews_by_type: dict
    ai_vs_human: dict

@router.get("/review-queue", response_model=List[QueueItemResponse])
async def get_review_queue(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    sort_by: str = Query("priority", pattern="^(priority|confidence|date)$"),
    db: Session = Depends(get_db)
):
    """
    Get review queue with case details for human reviewers.
    
    - **skip**: Number of items to skip (for pagination)
    - **limit**: Maximum number of items to return
    - **sort_by**: Sort order - 'priority', 'confidence', or 'date'
    """
    queue_items = crud.get_review_queue(db=db, skip=skip, limit=limit, sort_by=sort_by)
    return queue_items

@router.post("/review", response_model=ReviewResponse)
async def create_review(review: ReviewCreate, db: Session = Depends(get_db)):
    """
    Create a new review record for a case.
    """
    # Validate case exists based on case_type
    if review.case_type == "assessment":
        case = crud.get_assessment(db=db, assessment_id=review.case_id)
        if not case:
            raise HTTPException(status_code=404, detail="Assessment not found")
    elif review.case_type == "pdf_check":
        case = crud.get_pdf_check(db=db, pdf_check_id=review.case_id)
        if not case:
            raise HTTPException(status_code=404, detail="PDF check not found")
    else:
        raise HTTPException(status_code=400, detail="Invalid case_type")
    
    # Check if review already exists for this case
    existing_reviews = crud.get_reviews(db=db, limit=1000)  # Get all to check
    for existing in existing_reviews:
        if existing.case_id == review.case_id and existing.case_type == review.case_type:
            raise HTTPException(status_code=400, detail="Review already exists for this case")
    
    db_review = crud.create_review(
        db=db,
        case_id=review.case_id,
        case_type=review.case_type,
        reviewer_id=review.reviewer_id,
        ai_decision=review.ai_decision,
        decision=review.decision,
        notes=review.notes,
        human_decision=review.human_decision,
        ai_confidence=review.ai_confidence,
        priority=review.priority
    )
    return db_review

@router.put("/review/{review_id}", response_model=ReviewResponse)
async def update_review_decision(
    review_id: str,
    decision: ReviewDecision,
    db: Session = Depends(get_db)
):
    """
    Update a review with human decision.
    """
    db_review = crud.update_review_decision(
        db=db,
        review_id=review_id,
        decision=decision.decision,
        notes=decision.notes,
        human_decision=decision.human_decision
    )
    
    if db_review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    
    return db_review

@router.get("/review/{review_id}", response_model=ReviewResponse)
async def get_review(review_id: str, db: Session = Depends(get_db)):
    """
    Get a specific review by ID.
    """
    db_review = crud.get_review(db=db, review_id=review_id)
    if db_review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return db_review

@router.get("/reviews", response_model=List[ReviewResponse])
async def get_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None, pattern="^(pending|completed|escalated)$"),
    case_type: Optional[str] = Query(None, pattern="^(assessment|pdf_check|fraud_chain)$"),
    priority: Optional[str] = Query(None, pattern="^(low|medium|high)$"),
    db: Session = Depends(get_db)
):
    """
    Get all reviews with optional filtering.
    
    - **status**: Filter by review status
    - **case_type**: Filter by case type
    - **priority**: Filter by priority level
    """
    reviews = crud.get_reviews(
        db=db,
        skip=skip,
        limit=limit,
        status=status,
        case_type=case_type,
        priority=priority
    )
    return reviews

@router.post("/queue-low-confidence")
async def queue_low_confidence_cases(
    confidence_threshold: int = Query(70, ge=0, le=100),
    authenticity_threshold: int = Query(30, ge=0, le=100),
    db: Session = Depends(get_db)
):
    """
    Queue low-confidence AI decisions for human review.
    
    - **confidence_threshold**: Queue assessments below this confidence level
    - **authenticity_threshold**: Queue PDF checks below this authenticity score
    """
    assessment_count = crud.queue_low_confidence_assessments(db=db, confidence_threshold=confidence_threshold)
    pdf_count = crud.queue_suspicious_pdf_checks(db=db, authenticity_threshold=authenticity_threshold)
    
    return {
        "message": "Low confidence cases queued for review",
        "assessments_queued": assessment_count,
        "pdf_checks_queued": pdf_count,
        "total_queued": assessment_count + pdf_count
    }

@router.get("/statistics", response_model=ReviewStatisticsResponse)
async def get_review_statistics(db: Session = Depends(get_db)):
    """
    Get review system statistics including AI vs human decision metrics.
    """
    stats = crud.get_review_statistics(db=db)
    return stats