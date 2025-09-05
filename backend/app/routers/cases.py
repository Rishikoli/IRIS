from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, field_serializer
from datetime import datetime

from app.database import get_db
from app.models import InvestigationCase, CaseNote

router = APIRouter()

# Pydantic schemas
class CaseCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = "open"  # 'open', 'in_progress', 'closed'
    priority: Optional[str] = "medium"  # 'low', 'medium', 'high'
    assigned_to: Optional[str] = None
    related_entity_type: Optional[str] = None  # 'fraud_chain', 'assessment', 'pdf_check'
    related_entity_id: Optional[str] = None

class CaseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[str] = None

class CaseResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    status: str
    priority: str
    assigned_to: Optional[str]
    related_entity_type: Optional[str]
    related_entity_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat() if dt else ""

class NoteCreate(BaseModel):
    author: Optional[str] = None
    content: str

class NoteUpdate(BaseModel):
    author: Optional[str] = None
    content: Optional[str] = None

class NoteResponse(BaseModel):
    id: str
    case_id: str
    author: Optional[str]
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

    @field_serializer('created_at')
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat() if dt else ""

# Routes
@router.get("/cases", response_model=List[CaseResponse])
async def list_cases(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[str] = Query(None, pattern="^(open|in_progress|closed)$"),
    related_entity_type: Optional[str] = Query(None, pattern="^(fraud_chain|assessment|pdf_check)$"),
    related_entity_id: Optional[str] = None
):
    q = db.query(InvestigationCase)
    if status:
        q = q.filter(InvestigationCase.status == status)
    if related_entity_type:
        q = q.filter(InvestigationCase.related_entity_type == related_entity_type)
    if related_entity_id:
        q = q.filter(InvestigationCase.related_entity_id == related_entity_id)
    return q.order_by(InvestigationCase.created_at.desc()).offset(skip).limit(limit).all()

@router.post("/cases", response_model=CaseResponse)
async def create_case(payload: CaseCreate, db: Session = Depends(get_db)):
    # If a related entity is provided, ensure we don't duplicate cases for same entity + open status (optional policy)
    existing = None
    if payload.related_entity_type and payload.related_entity_id:
        existing = (
            db.query(InvestigationCase)
            .filter(InvestigationCase.related_entity_type == payload.related_entity_type)
            .filter(InvestigationCase.related_entity_id == payload.related_entity_id)
            .first()
        )
    if existing:
        return existing

    case = InvestigationCase(
        title=payload.title,
        description=payload.description,
        status=payload.status or "open",
        priority=payload.priority or "medium",
        assigned_to=payload.assigned_to,
        related_entity_type=payload.related_entity_type,
        related_entity_id=payload.related_entity_id,
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    return case

@router.get("/cases/{case_id}", response_model=CaseResponse)
async def get_case(case_id: str, db: Session = Depends(get_db)):
    case = db.query(InvestigationCase).get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@router.patch("/cases/{case_id}", response_model=CaseResponse)
async def update_case(case_id: str, payload: CaseUpdate, db: Session = Depends(get_db)):
    case = db.query(InvestigationCase).get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(case, field, value)
    db.add(case)
    db.commit()
    db.refresh(case)
    return case

@router.get("/cases/{case_id}/notes", response_model=List[NoteResponse])
async def list_notes(case_id: str, db: Session = Depends(get_db)):
    case = db.query(InvestigationCase).get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    notes = db.query(CaseNote).filter(CaseNote.case_id == case_id).order_by(CaseNote.created_at.desc()).all()
    return notes

@router.post("/cases/{case_id}/notes", response_model=NoteResponse)
async def add_note(case_id: str, payload: NoteCreate, db: Session = Depends(get_db)):
    case = db.query(InvestigationCase).get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    note = CaseNote(case_id=case_id, author=payload.author, content=payload.content)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

@router.patch("/cases/{case_id}/notes/{note_id}", response_model=NoteResponse)
async def update_note(case_id: str, note_id: str, payload: NoteUpdate, db: Session = Depends(get_db)):
    case = db.query(InvestigationCase).get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    note = db.query(CaseNote).get(note_id)
    if not note or note.case_id != case_id:
        raise HTTPException(status_code=404, detail="Note not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(note, field, value)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

@router.delete("/cases/{case_id}/notes/{note_id}")
async def delete_note(case_id: str, note_id: str, db: Session = Depends(get_db)):
    case = db.query(InvestigationCase).get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    note = db.query(CaseNote).get(note_id)
    if not note or note.case_id != case_id:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()
    return {"ok": True}
