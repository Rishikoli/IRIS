from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any
from pydantic import BaseModel
from app.database import get_db
from app.services.fraud_chain_service import FraudChainService

router = APIRouter()

# Response models
class RelationNode(BaseModel):
    id: str
    node_type: str
    reference_id: str
    label: str | None = None
    metadata: dict
    position_x: int | None = None
    position_y: int | None = None
    created_at: Any | None = None

class RelationEdge(BaseModel):
    id: str
    from_node_id: str
    to_node_id: str
    relationship_type: str
    confidence: int | None = None
    metadata: dict
    created_at: Any | None = None

class RelationsResponse(BaseModel):
    nodes: list[RelationNode]
    edges: list[RelationEdge]

@router.get("/relations/{entity_type}/{id}", response_model=RelationsResponse)
async def get_relations(
    entity_type: str,
    id: str,
    depth: int = Query(1, ge=1, le=3),
    limit: int = Query(100, ge=1, le=300),
    db: Session = Depends(get_db),
):
    """Return a bounded subgraph of related nodes/edges around a given entity reference.
    entity_type corresponds to FraudChainNode.node_type and id corresponds to reference_id.
    """
    service = FraudChainService(db)
    data = await service.get_relations_subgraph(entity_type=entity_type, reference_id=id, depth=depth, limit=limit)
    if data is None:
        raise HTTPException(status_code=404, detail="Relations not found")
    return data
