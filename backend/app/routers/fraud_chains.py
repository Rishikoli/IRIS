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
    created_at: Optional[datetime]

class FraudChainResponse(BaseModel):
    id: str
    name: Optional[str]
    description: Optional[str]
    status: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    nodes: List[FraudChainNodeResponse]
    edges: List[FraudChainEdgeResponse]

class FraudChainListResponse(BaseModel):
    id: str
    name: Optional[str]
    description: Optional[str]
    status: Optional[str]
    node_count: int
    edge_count: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

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

@router.post("/admin/demo/reset-graph")
async def reset_demo_graph(db: Session = Depends(get_db)):
    """Admin: Purge all chains and recreate a minimal demo chain.

    Returns: { message, deleted, chain_id, nodes, edges } or { error }
    """
    service = FraudChainService(db)
    result = await service.reset_demo_graph()
    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])
    return result

# Node-level search response models
class NodeSearchChainResult(BaseModel):
    chain_id: str
    reference_ids: List[str]
    count: int

class NodeSearchResponse(BaseModel):
    total: int
    took_ms: int
    used_backend: str
    results: List[NodeSearchChainResult]

@router.get("/fraud-chains/node-search", response_model=NodeSearchResponse)
async def search_chain_nodes(
    query: str = Query(..., min_length=1, description="Search query for nodes"),
    chain_id: Optional[str] = Query(None, description="Limit search to a specific chain"),
    limit_per_chain: int = Query(200, ge=1, le=1000, description="Max reference IDs to return per chain"),
    db: Session = Depends(get_db),
):
    """Search nodes by label, type, reference_id or metadata; returns reference IDs grouped by chain.

    This enables the frontend to highlight exact nodes and optionally zoom to them.
    """
    service = FraudChainService(db)
    result = await service.search_nodes(query=query, chain_id=chain_id, limit_per_chain=limit_per_chain)
    # Basic validation
    if result.get("error"):
        raise HTTPException(status_code=500, detail=str(result["error"]))
    return result

class UpsertEntityRequest(BaseModel):
    entity_type: str
    reference_id: str
    label: Optional[str] = None
    chain_id: Optional[str] = None
    create_new_chain: bool = True

class UpsertEntityResponse(BaseModel):
    chain_id: Optional[str] = None
    node_id: Optional[str] = None
    created: Optional[bool] = None
    error: Optional[str] = None

@router.post("/fraud-chains/upsert-entity", response_model=UpsertEntityResponse)
async def upsert_entity_into_chain(payload: UpsertEntityRequest, db: Session = Depends(get_db)):
    """Upsert a specific entity as a node into a fraud chain.

    Use when we want deterministic insertion of a searched item into a chain.
    """
    service = FraudChainService(db)
    result = await service.upsert_entity_into_chain(
        entity_type=payload.entity_type,
        reference_id=payload.reference_id,
        label=payload.label,
        chain_id=payload.chain_id,
        create_new_chain=payload.create_new_chain,
    )
    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])
    return result