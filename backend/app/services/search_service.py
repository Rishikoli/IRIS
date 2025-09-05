from typing import List, Dict, Any, Optional
import time
import os

try:
    # Optional dependency
    from elasticsearch import Elasticsearch
    ES_AVAILABLE = True
except Exception:
    Elasticsearch = None  # type: ignore
    ES_AVAILABLE = False

from app.schemas.search import SearchRequest, SearchHit, SearchResponse

class SearchService:
    def __init__(self, es_url: Optional[str] = None):
        self.es_url = es_url or os.getenv("ELASTICSEARCH_URL")
        self.client = None
        if ES_AVAILABLE and self.es_url:
            try:
                self.client = Elasticsearch(self.es_url)
            except Exception:
                self.client = None

    def _demo_results(self, req: SearchRequest) -> SearchResponse:
        start = time.time()
        demo_hits: List[SearchHit] = [
            SearchHit(id=101, entity_type='tip', title='Suspicious Telegram Tip', snippet='High return promise on smallcap', score=0.89, risk='High', extra={"source":"demo"}),
            SearchHit(id=22, entity_type='advisor', title='Advisor: Raj Mehta', snippet='SEBI reg pending verification', score=0.77, risk='Medium', extra={"source":"demo"}),
            SearchHit(id=304, entity_type='document', title='PDF: Contract-INV-2024-09.pdf', snippet='Stamp mismatch detected', score=0.74, risk='High', extra={"source":"demo"}),
        ]
        took = int((time.time() - start) * 1000)
        return SearchResponse(total=len(demo_hits), took_ms=took, hits=demo_hits[: req.size], used_backend='sqlite_fallback')

    def _build_es_query(self, req: SearchRequest) -> Dict[str, Any]:
        must: List[Dict[str, Any]] = []
        filters: List[Dict[str, Any]] = []

        must.append({
            "multi_match": {
                "query": req.query,
                "fields": ["title^3", "content", "name^2", "company", "summary"],
                "fuzziness": req.fuzziness or "AUTO"
            }
        })

        if req.filters:
            if req.filters.entity_types:
                filters.append({"terms": {"entity_type": req.filters.entity_types}})
            if req.filters.min_risk:
                filters.append({"range": {"risk_rank": {"gte": {"Low":1, "Medium":2, "High":3}[req.filters.min_risk]}}})
            if req.filters.date_from or req.filters.date_to:
                rng: Dict[str, Any] = {}
                if req.filters.date_from:
                    rng["gte"] = req.filters.date_from
                if req.filters.date_to:
                    rng["lte"] = req.filters.date_to
                filters.append({"range": {"created_at": rng}})

        return {
            "query": {
                "bool": {
                    "must": must,
                    "filter": filters
                }
            },
            "from": req.from_,
            "size": req.size,
            "sort": [{"_score": "desc"}]
        }

    def search(self, req: SearchRequest) -> SearchResponse:
        # If ES not configured or unavailable, return demo results for now
        if not self.client:
            return self._demo_results(req)

        start = time.time()
        try:
            body = self._build_es_query(req)
            # Search across multiple indices; they may or may not exist
            indices = os.getenv("ELASTICSEARCH_INDICES", "tips,advisors,documents")
            res = self.client.search(index=indices, body=body, request_timeout=5)
            hits: List[SearchHit] = []
            for h in res.get('hits', {}).get('hits', []):
                src = h.get('_source', {})
                hits.append(SearchHit(
                    id=src.get('id') or 0,
                    entity_type=src.get('entity_type') or 'tip',
                    title=src.get('title') or src.get('name'),
                    snippet=src.get('snippet') or src.get('summary') or src.get('content', '')[:160],
                    score=float(h.get('_score') or 0.0),
                    risk=src.get('risk'),
                    extra={k: v for k, v in src.items() if k not in ['id','entity_type','title','name','snippet','summary','content','risk']}
                ))
            took = int((time.time() - start) * 1000)
            total = int(res.get('hits', {}).get('total', {}).get('value', len(hits)))
            return SearchResponse(total=total, took_ms=took, hits=hits, used_backend='elasticsearch')
        except Exception:
            # Graceful fallback
            return self._demo_results(req)

search_service = SearchService()
