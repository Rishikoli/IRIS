from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.services.fraud_chain_service import FraudChainService
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# Response models
class FraudChainNodeResponse(BaseModel):
    id: str
    node_type: str
    reference_id: str
    label: Optional[str]
    metadata: dict
    position_x: Optional[int]
    position_y: Optional[int]
    created_at: datetime

class FraudChainEdgeResponse(BaseModel):
    id: str
    from_node_id: str
    to_node_id: str
    relationship_type: str
    confidence: int
    metadata: dict
    created_at: datetime

class FraudChainResponse(BaseModel):
    id: str
    name: Optional[str]
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    nodes: List[FraudChainNodeResponse]
    edges: List[FraudChainEdgeResponse]

class FraudChainListResponse(BaseModel):
    id: str
    name: Optional[str]
    description: Optional[str]
    status: str
    node_count: int
    edge_count: int
    created_at: datetime
    updated_at: datetime

@router.get("/fraud-chains", response_model=List[FraudChainListResponse])
async def get_fraud_chains(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get list of fraud chains with basic information"""
    service = FraudChainService(db)
    return await service.get_fraud_chains(status=status, limit=limit, offset=offset)

@router.get("/fraud-chain/{chain_id}", response_model=FraudChainResponse)
async def get_fraud_chain(
    chain_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed fraud chain with nodes and edges"""
    service = FraudChainService(db)
    chain = await service.get_fraud_chain_by_id(chain_id)
    
    if not chain:
        raise HTTPException(status_code=404, detail="Fraud chain not found")
    
    return chain

@router.post("/fraud-chain/{chain_id}/export")
async def export_fraud_chain(
    chain_id: str,
    format: str = Query("json", pattern="^(json|csv)$"),
    db: Session = Depends(get_db)
):
    """Export fraud chain data in specified format"""
    service = FraudChainService(db)
    
    chain = await service.get_fraud_chain_by_id(chain_id)
    if not chain:
        raise HTTPException(status_code=404, detail="Fraud chain not found")
    
    if format == "json":
        return await service.export_chain_json(chain_id)
    elif format == "csv":
        return await service.export_chain_csv(chain_id)

@router.post("/fraud-chains/auto-link")
async def auto_link_fraud_cases(
    db: Session = Depends(get_db)
):
    """Automatically link related fraud cases into chains"""
    service = FraudChainService(db)
    result = await service.auto_link_fraud_cases()
    
    return {
        "message": "Auto-linking completed",
        "chains_created": result.get("chains_created", 0),
        "links_added": result.get("links_added", 0)
    }