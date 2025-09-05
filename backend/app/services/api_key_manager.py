"""
API Key Management and Fallback Service
Manages API keys, monitors usage, and provides fallback mechanisms
"""

import os
import asyncio
from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta
from pydantic import BaseModel
import json
from app.services.cache_service import cache_service

class APIKeyStatus(BaseModel):
    service: str
    key_id: str
    is_valid: bool
    last_checked: datetime
    error_count: int
    rate_limit_reset: Optional[datetime] = None
    daily_usage: int = 0
    monthly_usage: int = 0

class ServiceHealth(BaseModel):
    service: str
    status: str  # 'healthy', 'degraded', 'down'
    response_time_ms: float
    error_rate: float
    last_success: Optional[datetime] = None
    last_error: Optional[datetime] = None

class APIKeyManager:
    """Manages API keys and service health monitoring"""
    
    def __init__(self):
        # API key configuration
        self.api_keys = {
            "fmp": {
                "primary": os.getenv("FMP_API_KEY", "demo"),
                "fallback": os.getenv("FMP_API_KEY_FALLBACK", ""),
                "rate_limit_per_minute": int(os.getenv("FMP_RATE_LIMIT_PER_MINUTE", "60")),
                "monthly_limit": int(os.getenv("FMP_MONTHLY_LIMIT", "10000"))
            },
            "gemini": {
                "primary": os.getenv("GEMINI_API_KEY", ""),
                "fallback": os.getenv("GEMINI_API_KEY_FALLBACK", ""),
                "rate_limit_per_minute": int(os.getenv("GEMINI_RATE_LIMIT_PER_MINUTE", "60")),
                "monthly_limit": int(os.getenv("GEMINI_MONTHLY_LIMIT", "1000"))
            }
        }
        
        # Service health tracking
        self.service_health: Dict[str, ServiceHealth] = {}
        
        # Error thresholds
        self.error_threshold = 5  # Switch to fallback after 5 errors
        self.health_check_interval = 300  # 5 minutes
        
    async def get_api_key(self, service: str) -> Optional[str]:
        """Get the best available API key for a service"""
        if service not in self.api_keys:
            return None
        
        service_config = self.api_keys[service]
        
        # Check primary key status
        primary_status = await self._get_key_status(service, "primary")
        
        if primary_status.is_valid and primary_status.error_count < self.error_threshold:
            return service_config["primary"]
        
        # Try fallback key if primary is failing
        if service_config.get("fallback"):
            fallback_status = await self._get_key_status(service, "fallback")
            if fallback_status.is_valid and fallback_status.error_count < self.error_threshold:
                return service_config["fallback"]
        
        # Return primary even if degraded (better than nothing)
        return service_config["primary"] if service_config["primary"] != "demo" else None
    
    async def _get_key_status(self, service: str, key_type: str) -> APIKeyStatus:
        """Get or create API key status"""
        cache_key = f"api_key_status:{service}:{key_type}"
        
        cached_status = await cache_service.get(cache_key)
        if cached_status:
            return APIKeyStatus(**cached_status)
        
        # Create new status
        status = APIKeyStatus(
            service=service,
            key_id=key_type,
            is_valid=True,
            last_checked=datetime.now(),
            error_count=0,
            daily_usage=0,
            monthly_usage=0
        )
        
        # Cache for 1 hour
        await cache_service.set(cache_key, status.model_dump(), 3600, "api_key_manager")
        
        return status
    
    async def record_api_success(self, service: str, key_type: str = "primary", response_time_ms: float = 0):
        """Record successful API call"""
        # Update key status
        status = await self._get_key_status(service, key_type)
        status.last_checked = datetime.now()
        status.error_count = max(0, status.error_count - 1)  # Reduce error count on success
        status.daily_usage += 1
        status.monthly_usage += 1
        
        await self._save_key_status(status)
        
        # Update service health
        await self._update_service_health(service, True, response_time_ms)
    
    async def record_api_error(self, service: str, key_type: str = "primary", error: str = ""):
        """Record API error"""
        # Update key status
        status = await self._get_key_status(service, key_type)
        status.last_checked = datetime.now()
        status.error_count += 1
        
        # Mark as invalid if too many errors
        if status.error_count >= self.error_threshold:
            status.is_valid = False
        
        await self._save_key_status(status)
        
        # Update service health
        await self._update_service_health(service, False, 0, error)
    
    async def _save_key_status(self, status: APIKeyStatus):
        """Save API key status to cache"""
        cache_key = f"api_key_status:{status.service}:{status.key_id}"
        await cache_service.set(cache_key, status.model_dump(), 3600, "api_key_manager")
    
    async def _update_service_health(self, service: str, success: bool, response_time_ms: float, error: str = ""):
        """Update service health metrics"""
        if service not in self.service_health:
            self.service_health[service] = ServiceHealth(
                service=service,
                status="healthy",
                response_time_ms=0,
                error_rate=0
            )
        
        health = self.service_health[service]
        
        if success:
            health.last_success = datetime.now()
            health.response_time_ms = (health.response_time_ms + response_time_ms) / 2  # Moving average
            
            # Improve status if it was degraded
            if health.status == "degraded":
                health.status = "healthy"
        else:
            health.last_error = datetime.now()
            
            # Degrade status based on error frequency
            if health.status == "healthy":
                health.status = "degraded"
            elif health.status == "degraded":
                health.status = "down"
        
        # Calculate error rate (simplified)
        if health.last_success and health.last_error:
            time_window = timedelta(hours=1)
            if datetime.now() - health.last_error < time_window:
                health.error_rate = min(1.0, health.error_rate + 0.1)
            else:
                health.error_rate = max(0.0, health.error_rate - 0.05)
    
    async def get_service_health(self, service: str) -> Optional[ServiceHealth]:
        """Get current service health status"""
        return self.service_health.get(service)
    
    async def get_all_service_health(self) -> Dict[str, ServiceHealth]:
        """Get health status for all services"""
        return self.service_health.copy()
    
    async def is_service_available(self, service: str) -> bool:
        """Check if service is available for use"""
        health = await self.get_service_health(service)
        if not health:
            return True  # Assume available if no health data
        
        return health.status != "down"
    
    async def get_fallback_strategy(self, service: str) -> Dict[str, Any]:
        """Get fallback strategy for a service"""
        strategies = {
            "fmp": {
                "use_cache": True,
                "cache_ttl_extended": 3600,  # 1 hour instead of 5 minutes
                "mock_data": True,
                "alternative_sources": ["yahoo_finance", "alpha_vantage"]
            },
            "gemini": {
                "use_cache": True,
                "cache_ttl_extended": 7200,  # 2 hours
                "mock_analysis": True,
                "alternative_models": ["openai", "claude"]
            },
            "trends": {
                "use_cache": True,
                "cache_ttl_extended": 7200,  # 2 hours
                "mock_data": True,
                "alternative_sources": ["google_news", "social_media"]
            },
            "scraping": {
                "use_cache": True,
                "cache_ttl_extended": 3600,  # 1 hour
                "mock_data": True,
                "alternative_sources": ["rss_feeds", "news_apis"]
            }
        }
        
        return strategies.get(service, {
            "use_cache": True,
            "cache_ttl_extended": 3600,
            "mock_data": True
        })
    
    async def reset_service_health(self, service: str):
        """Reset service health status (for manual recovery)"""
        if service in self.service_health:
            self.service_health[service].status = "healthy"
            self.service_health[service].error_rate = 0
            self.service_health[service].last_error = None
        
        # Reset API key error counts
        for key_type in ["primary", "fallback"]:
            status = await self._get_key_status(service, key_type)
            status.error_count = 0
            status.is_valid = True
            await self._save_key_status(status)
    
    async def get_usage_stats(self, service: str) -> Dict[str, Any]:
        """Get API usage statistics"""
        primary_status = await self._get_key_status(service, "primary")
        fallback_status = await self._get_key_status(service, "fallback")
        
        service_config = self.api_keys.get(service, {})
        
        return {
            "service": service,
            "primary_key": {
                "daily_usage": primary_status.daily_usage,
                "monthly_usage": primary_status.monthly_usage,
                "monthly_limit": service_config.get("monthly_limit", 0),
                "usage_percentage": (primary_status.monthly_usage / service_config.get("monthly_limit", 1)) * 100
            },
            "fallback_key": {
                "daily_usage": fallback_status.daily_usage,
                "monthly_usage": fallback_status.monthly_usage,
                "available": bool(service_config.get("fallback"))
            },
            "health": await self.get_service_health(service)
        }
    
    async def validate_api_key(self, service: str, api_key: str) -> bool:
        """Validate an API key by making a test request"""
        # This would make actual test requests to validate keys
        # For now, return True for non-demo keys
        return api_key and api_key != "demo" and len(api_key) > 10

# Global instance
api_key_manager = APIKeyManager()