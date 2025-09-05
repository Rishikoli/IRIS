from typing import List, Optional, Literal
from pydantic import BaseModel, Field

# Request schemas
class SearchFilter(BaseModel):
    entity_types: Optional[List[Literal['tip','advisor','document']]] = Field(default=None, description="Entities to search")
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    min_risk: Optional[Literal['Low','Medium','High']] = None

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    filters: Optional[SearchFilter] = None
    fuzziness: Optional[str] = Field(default="AUTO", description="Elasticsearch fuzziness or fallback similarity")
    size: int = Field(default=25, ge=1, le=200)
    from_: int = Field(default=0, ge=0, alias="from")

    class Config:
        allow_population_by_field_name = True

# Response schemas
class SearchHit(BaseModel):
    id: int
    entity_type: Literal['tip','advisor','document']
    title: Optional[str] = None
    snippet: Optional[str] = None
    score: float
    risk: Optional[Literal['Low','Medium','High']] = None
    extra: Optional[dict] = None

class SearchResponse(BaseModel):
    total: int
    took_ms: int
    hits: List[SearchHit]
    used_backend: Literal['elasticsearch','sqlite_fallback']
