from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.schemas.search import SearchRequest, SearchResponse
from app.services.search_service import search_service

router = APIRouter()

@router.post("/search", response_model=SearchResponse)
def search_endpoint(payload: SearchRequest) -> Dict[str, Any]:
    try:
        result = search_service.search(payload)
        return result.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
