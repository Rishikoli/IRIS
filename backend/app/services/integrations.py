#!/usr/bin/env python3
"""
External integrations for Analytics: Gemini (LLM) and FMP (market data)
"""
from __future__ import annotations
import os
import time
from typing import Any, Dict, List, Optional

# HTTP client
try:
    import requests
except Exception:  # pragma: no cover
    requests = None  # type: ignore

# Optional Gemini SDK
try:
    import google.generativeai as genai  # type: ignore
except Exception:  # pragma: no cover
    genai = None  # type: ignore


class _TTLCache:
    def __init__(self, ttl_seconds: int = 300):
        self.ttl = ttl_seconds
        self._store: Dict[str, Any] = {}
        self._ts: Dict[str, float] = {}

    def get(self, key: str) -> Optional[Any]:
        now = time.time()
        ts = self._ts.get(key)
        if ts is None or (now - ts) > self.ttl:
            return None
        return self._store.get(key)

    def set(self, key: str, value: Any) -> None:
        self._store[key] = value
        self._ts[key] = time.time()


class FMPClient:
    BASE_URL = "https://financialmodelingprep.com/api/v3"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("FMP_API_KEY")
        self._cache = _TTLCache(ttl_seconds=300)

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        if requests is None:
            return {"error": "requests not installed"}
        params = params or {}
        if self.api_key:
            params["apikey"] = self.api_key
        url = f"{self.BASE_URL}/{path.lstrip('/')}"
        cache_key = f"GET:{url}:{sorted(params.items())}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            self._cache.set(cache_key, data)
            return data
        except Exception as e:
            return {"error": str(e)}

    def get_sector_performance(self) -> Any:
        # FMP endpoint example: /stock/sectors-performance
        return self._get("stock/sectors-performance")

    def search_news(self, query: str, limit: int = 20) -> Any:
        # /search-news?query=...&limit=...
        return self._get("search-news", {"query": query, "limit": limit})


class GeminiClient:
    DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model or self.DEFAULT_MODEL
        self._ready = False
        if genai and self.api_key:
            try:  # lazy configure
                genai.configure(api_key=self.api_key)
                self._ready = True
            except Exception:
                self._ready = False

    def generate_insights(self, prompt: str) -> Optional[str]:
        if not self._ready or not genai:
            return None
        try:
            model = genai.GenerativeModel(self.model)
            res = model.generate_content(prompt)
            text = getattr(res, "text", None)
            if text:
                return text.strip()
            # SDK may return candidates
            cand = getattr(res, "candidates", None)
            if cand and len(cand) and getattr(cand[0], "content", None):
                parts = getattr(cand[0].content, "parts", [])
                combined = "\n".join(getattr(p, "text", "") for p in parts if getattr(p, "text", ""))
                return combined.strip() or None
            return None
        except Exception:
            return None


# Singletons
fmp_client = FMPClient()
gemini_client = GeminiClient()
