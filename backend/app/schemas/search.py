from typing import List, Optional, Literal, Dict
from pydantic import BaseModel, Field, field_validator

# Request schemas
class SearchFilter(BaseModel):
    entity_types: Optional[List[Literal['tip','advisor','document','assessment']]] = Field(default=None, description="Entities to search (legacy; prefer top-level 'entities')")
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    min_risk: Optional[Literal['Low','Medium','High']] = None
    sector: Optional[List[str]] = None
    region: Optional[List[str]] = None
    risk_levels: Optional[List[Literal['Low','Medium','High']]] = None

class FuzzyOptions(BaseModel):
    enabled: bool = True
    max_edits: Optional[int] = Field(default=None, ge=0, le=2, description="Max Levenshtein edits; if None, uses AUTO")

class XrefOptions(BaseModel):
    enabled: bool = False
    link_depth: int = Field(default=0, ge=0, le=2)

class RankingBoost(BaseModel):
    risk_score: Optional[float] = 1.0
    recentness: Optional[float] = 1.0
    entity_weights: Optional[Dict[str, float]] = None

class RankingOptions(BaseModel):
    boost: Optional[RankingBoost] = None

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    # New: top-level entity selection; kept optional for backward compatibility
    entities: Optional[List[Literal['tips','advisors','documents','assessments']]] = Field(default=None)
    filters: Optional[SearchFilter] = None
    # Legacy fuzziness string retained; new fuzzy options preferred
    fuzziness: Optional[str] = Field(default="AUTO", description="Elasticsearch fuzziness or fallback similarity")
    fuzzy: Optional[FuzzyOptions] = None
    xref: Optional[XrefOptions] = None
    ranking: Optional[RankingOptions] = None
    # Pagination: prefer page/page_size; keep from/size for compatibility
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    size: int = Field(default=25, ge=1, le=200)
    from_: int = Field(default=0, ge=0, alias="from")
    save_history: Optional[bool] = False

    class Config:
        allow_population_by_field_name = True

    @field_validator('page_size')
    @classmethod
    def page_size_cap(cls, v):
        return min(v, 100)

# Response schemas
class SearchHit(BaseModel):
    id: int
    entity_type: Literal['tip','advisor','document','assessment']
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
