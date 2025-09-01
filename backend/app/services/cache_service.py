"""
Caching and Rate Limiting Service for Real-Time Data Integration
Provides caching, rate limiting, and data freshness management
"""

import asyncio
import json
import time
from typing import Any, Dict, Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel
import hashlib
import os

# Try to import Redis for production caching
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

class CacheEntry(BaseModel):
    data: Any
    timestamp: datetime
    ttl_seconds: int
    source: str

class RateLimitEntry(BaseModel):
    count: int
    window_start: datetime
    limit: int
    window_seconds: int

class CacheService:
    """Caching service with Redis fallback to in-memory cache"""
    
    def __init__(self):
        self.use_redis = REDIS_AVAILABLE and os.getenv("REDIS_URL")
        self.default_ttl = int(os.getenv("CACHE_TTL_SECONDS", "300"))  # 5 minutes
        
        # In-memory cache fallback
        self._memory_cache: Dict[str, CacheEntry] = {}
        self._rate_limits: Dict[str, RateLimitEntry] = {}
        
        if self.use_redis:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            self.redis_client = redis.from_url(redis_url)
        else:
            self.redis_client = None
    
    async def get(self, key: str) -> Optional[Any]:
        """Get cached data by key"""
        try:
            if self.use_redis and self.redis_client:
                return await self._get_from_redis(key)
            else:
                return await self._get_from_memory(key)
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, data: Any, ttl_seconds: Optional[int] = None, source: str = "unknown") -> bool:
        """Set cached data with TTL"""
        try:
            ttl = ttl_seconds or self.default_ttl
            
            if self.use_redis and self.redis_client:
                return await self._set_to_redis(key, data, ttl, source)
            else:
                return await self._set_to_memory(key, data, ttl, source)
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete cached data"""
        try:
            if self.use_redis and self.redis_client:
                result = await self.redis_client.delete(key)
                return result > 0
            else:
                if key in self._memory_cache:
                    del self._memory_cache[key]
                    return True
                return False
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    async def clear_expired(self):
        """Clear expired cache entries (for memory cache)"""
        if not self.use_redis:
            current_time = datetime.now()
            expired_keys = []
            
            for key, entry in self._memory_cache.items():
                if current_time > entry.timestamp + timedelta(seconds=entry.ttl_seconds):
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._memory_cache[key]
    
    async def _get_from_redis(self, key: str) -> Optional[Any]:
        """Get data from Redis cache"""
        cached_data = await self.redis_client.get(key)
        if cached_data:
            try:
                entry_dict = json.loads(cached_data)
                return entry_dict.get('data')
            except json.JSONDecodeError:
                return None
        return None
    
    async def _set_to_redis(self, key: str, data: Any, ttl: int, source: str) -> bool:
        """Set data to Redis cache"""
        entry = CacheEntry(
            data=data,
            timestamp=datetime.now(),
            ttl_seconds=ttl,
            source=source
        )
        
        try:
            serialized_data = json.dumps(entry.model_dump(), default=str)
            await self.redis_client.setex(key, ttl, serialized_data)
            return True
        except (json.JSONEncodeError, TypeError):
            return False
    
    async def _get_from_memory(self, key: str) -> Optional[Any]:
        """Get data from memory cache"""
        if key in self._memory_cache:
            entry = self._memory_cache[key]
            current_time = datetime.now()
            
            # Check if expired
            if current_time > entry.timestamp + timedelta(seconds=entry.ttl_seconds):
                del self._memory_cache[key]
                return None
            
            return entry.data
        return None
    
    async def _set_to_memory(self, key: str, data: Any, ttl: int, source: str) -> bool:
        """Set data to memory cache"""
        entry = CacheEntry(
            data=data,
            timestamp=datetime.now(),
            ttl_seconds=ttl,
            source=source
        )
        self._memory_cache[key] = entry
        return True
    
    def generate_cache_key(self, service: str, method: str, params: Dict[str, Any]) -> str:
        """Generate a consistent cache key"""
        # Create a hash of the parameters for consistent keys
        params_str = json.dumps(params, sort_keys=True, default=str)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
        return f"{service}:{method}:{params_hash}"

class RateLimitService:
    """Rate limiting service for API calls"""
    
    def __init__(self):
        self._rate_limits: Dict[str, RateLimitEntry] = {}
        
        # Default rate limits
        self.default_limits = {
            "fmp": int(os.getenv("FMP_RATE_LIMIT_PER_MINUTE", "60")),
            "trends": int(os.getenv("TRENDS_RATE_LIMIT_PER_HOUR", "100")),
            "scraping": 60  # 1 request per second
        }
    
    async def check_rate_limit(self, service: str, identifier: str = "default") -> bool:
        """Check if request is within rate limit"""
        key = f"{service}:{identifier}"
        current_time = datetime.now()
        
        # Get service-specific limits
        if service == "fmp":
            limit = self.default_limits["fmp"]
            window_seconds = 60  # 1 minute
        elif service == "trends":
            limit = self.default_limits["trends"]
            window_seconds = 3600  # 1 hour
        elif service == "scraping":
            limit = self.default_limits["scraping"]
            window_seconds = 60  # 1 minute
        else:
            limit = 100
            window_seconds = 3600
        
        if key not in self._rate_limits:
            # First request
            self._rate_limits[key] = RateLimitEntry(
                count=1,
                window_start=current_time,
                limit=limit,
                window_seconds=window_seconds
            )
            return True
        
        entry = self._rate_limits[key]
        
        # Check if window has expired
        if current_time > entry.window_start + timedelta(seconds=entry.window_seconds):
            # Reset window
            entry.count = 1
            entry.window_start = current_time
            return True
        
        # Check if within limit
        if entry.count < entry.limit:
            entry.count += 1
            return True
        
        return False
    
    async def get_rate_limit_status(self, service: str, identifier: str = "default") -> Dict[str, Any]:
        """Get current rate limit status"""
        key = f"{service}:{identifier}"
        
        if key not in self._rate_limits:
            return {
                "requests_made": 0,
                "limit": self.default_limits.get(service, 100),
                "window_seconds": 3600,
                "reset_time": None
            }
        
        entry = self._rate_limits[key]
        reset_time = entry.window_start + timedelta(seconds=entry.window_seconds)
        
        return {
            "requests_made": entry.count,
            "limit": entry.limit,
            "window_seconds": entry.window_seconds,
            "reset_time": reset_time.isoformat(),
            "requests_remaining": max(0, entry.limit - entry.count)
        }

class DataFreshnessService:
    """Service to manage data freshness and validation"""
    
    def __init__(self, cache_service: CacheService):
        self.cache_service = cache_service
        
        # Freshness thresholds (in seconds)
        self.freshness_thresholds = {
            "market_data": 300,      # 5 minutes
            "news_data": 1800,       # 30 minutes
            "trends_data": 3600,     # 1 hour
            "company_profile": 86400, # 24 hours
        }
    
    async def is_data_fresh(self, data_type: str, key: str) -> bool:
        """Check if cached data is still fresh"""
        threshold = self.freshness_thresholds.get(data_type, 3600)
        
        # Try to get cache metadata
        cache_key = f"meta:{key}"
        metadata = await self.cache_service.get(cache_key)
        
        if not metadata:
            return False
        
        cached_time = datetime.fromisoformat(metadata.get("timestamp", ""))
        current_time = datetime.now()
        
        return (current_time - cached_time).total_seconds() < threshold
    
    async def mark_data_fresh(self, data_type: str, key: str, source: str):
        """Mark data as fresh with current timestamp"""
        cache_key = f"meta:{key}"
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "data_type": data_type,
            "source": source
        }
        
        threshold = self.freshness_thresholds.get(data_type, 3600)
        await self.cache_service.set(cache_key, metadata, threshold, source)
    
    async def get_data_quality_score(self, data: Any, data_type: str) -> float:
        """Calculate data quality score (0-100)"""
        score = 100.0
        
        # Basic data validation
        if not data:
            return 0.0
        
        if isinstance(data, list):
            if len(data) == 0:
                return 0.0
            
            # Check for completeness
            if data_type == "market_data":
                required_fields = ["symbol", "price", "volume"]
                for item in data[:5]:  # Check first 5 items
                    if isinstance(item, dict):
                        missing_fields = [field for field in required_fields if not item.get(field)]
                        if missing_fields:
                            score -= 10
            
            elif data_type == "news_data":
                required_fields = ["title", "content", "published_at"]
                for item in data[:5]:
                    if isinstance(item, dict):
                        missing_fields = [field for field in required_fields if not item.get(field)]
                        if missing_fields:
                            score -= 10
        
        return max(0.0, min(100.0, score))

# Global service instances
cache_service = CacheService()
rate_limit_service = RateLimitService()
data_freshness_service = DataFreshnessService(cache_service)