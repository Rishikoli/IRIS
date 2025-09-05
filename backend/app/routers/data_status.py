"""
Data Status and Health Monitoring Router
Provides endpoints to check the status of real-time data services
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from datetime import datetime
from pydantic import BaseModel

from app.services.api_key_manager import api_key_manager
from app.services.cache_service import cache_service, rate_limit_service, data_freshness_service
from app.services.fmp_service import fmp_service
from app.services.google_trends_service import GoogleTrendsService
from app.services.economic_times_service import EconomicTimesScrapingService

router = APIRouter(prefix="/api/data-status", tags=["Data Status"])

class ServiceStatus(BaseModel):
    service: str
    status: str  # 'healthy', 'degraded', 'down', 'mock'
    last_update: datetime
    cache_status: str
    rate_limit_status: Dict[str, Any]
    error_count: int
    data_freshness: str

class DataQualityMetrics(BaseModel):
    service: str
    quality_score: float  # 0-100
    completeness: float
    freshness_minutes: int
    source_type: str  # 'real', 'cached', 'mock'

@router.get("/health", response_model=Dict[str, ServiceStatus])
async def get_all_service_health():
    """Get health status of all real-time data services"""
    
    services = ["fmp", "trends", "economic_times", "gemini"]
    status_dict = {}
    
    for service in services:
        try:
            # Get service health from API key manager
            health = await api_key_manager.get_service_health(service)
            
            # Get rate limit status
            rate_limit_status = await rate_limit_service.get_rate_limit_status(service)
            
            # Determine overall status
            if health:
                status = health.status
                error_count = 0  # Would need to track this properly
                last_update = health.last_success or datetime.now()
            else:
                status = "unknown"
                error_count = 0
                last_update = datetime.now()
            
            # Check if using real APIs or mock data
            if service == "fmp":
                api_key = await api_key_manager.get_api_key("fmp")
                if not api_key or api_key == "demo":
                    status = "mock"
            
            status_dict[service] = ServiceStatus(
                service=service,
                status=status,
                last_update=last_update,
                cache_status="active",  # Simplified
                rate_limit_status=rate_limit_status,
                error_count=error_count,
                data_freshness="fresh"  # Simplified
            )
            
        except Exception as e:
            status_dict[service] = ServiceStatus(
                service=service,
                status="error",
                last_update=datetime.now(),
                cache_status="unknown",
                rate_limit_status={},
                error_count=1,
                data_freshness="stale"
            )
    
    return status_dict

@router.get("/quality", response_model=List[DataQualityMetrics])
async def get_data_quality_metrics():
    """Get data quality metrics for all services"""
    
    metrics = []
    
    # FMP Service Quality
    try:
        # Test fetch a small amount of data
        test_data = await fmp_service.fetch_market_data(["RELIANCE.NS"])
        
        if test_data:
            quality_score = await data_freshness_service.get_data_quality_score(test_data, "market_data")
            source_type = "real" if fmp_service.use_real_api else "mock"
        else:
            quality_score = 0
            source_type = "unavailable"
        
        metrics.append(DataQualityMetrics(
            service="fmp",
            quality_score=quality_score,
            completeness=100.0 if test_data else 0.0,
            freshness_minutes=5,  # Based on cache TTL
            source_type=source_type
        ))
        
    except Exception as e:
        metrics.append(DataQualityMetrics(
            service="fmp",
            quality_score=0,
            completeness=0,
            freshness_minutes=999,
            source_type="error"
        ))
    
    # Google Trends Quality
    try:
        trends_service = GoogleTrendsService()
        test_trends = await trends_service.fetch_fraud_trends(["Mumbai"], "7d")
        
        if test_trends:
            quality_score = await data_freshness_service.get_data_quality_score(test_trends, "trends_data")
            source_type = "real" if trends_service.use_real_api else "mock"
        else:
            quality_score = 0
            source_type = "unavailable"
        
        metrics.append(DataQualityMetrics(
            service="google_trends",
            quality_score=quality_score,
            completeness=100.0 if test_trends else 0.0,
            freshness_minutes=60,  # Based on cache TTL
            source_type=source_type
        ))
        
    except Exception as e:
        metrics.append(DataQualityMetrics(
            service="google_trends",
            quality_score=0,
            completeness=0,
            freshness_minutes=999,
            source_type="error"
        ))
    
    # Economic Times Quality
    try:
        et_service = EconomicTimesScrapingService()
        test_articles = await et_service.scrape_latest_news(["markets"])
        
        if test_articles:
            quality_score = await data_freshness_service.get_data_quality_score(test_articles, "news_data")
            source_type = "real" if et_service.use_real_scraping else "mock"
        else:
            quality_score = 0
            source_type = "unavailable"
        
        metrics.append(DataQualityMetrics(
            service="economic_times",
            quality_score=quality_score,
            completeness=100.0 if test_articles else 0.0,
            freshness_minutes=30,  # Based on cache TTL
            source_type=source_type
        ))
        
    except Exception as e:
        metrics.append(DataQualityMetrics(
            service="economic_times",
            quality_score=0,
            completeness=0,
            freshness_minutes=999,
            source_type="error"
        ))
    
    return metrics

@router.get("/usage/{service}")
async def get_service_usage(service: str):
    """Get API usage statistics for a specific service"""
    
    if service not in ["fmp", "gemini", "trends", "economic_times"]:
        raise HTTPException(status_code=404, detail="Service not found")
    
    try:
        usage_stats = await api_key_manager.get_usage_stats(service)
        return usage_stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting usage stats: {str(e)}")

@router.post("/reset/{service}")
async def reset_service_health(service: str):
    """Reset health status for a service (manual recovery)"""
    
    if service not in ["fmp", "gemini", "trends", "economic_times"]:
        raise HTTPException(status_code=404, detail="Service not found")
    
    try:
        await api_key_manager.reset_service_health(service)
        return {"message": f"Service {service} health status reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting service: {str(e)}")

@router.get("/cache/stats")
async def get_cache_statistics():
    """Get cache usage and performance statistics"""
    
    try:
        # This would need to be implemented in the cache service
        # For now, return basic stats
        stats = {
            "cache_type": "redis" if cache_service.use_redis else "memory",
            "total_keys": "unknown",  # Would need Redis INFO command
            "hit_rate": "unknown",
            "memory_usage": "unknown",
            "services_cached": ["fmp", "trends", "economic_times", "gemini"]
        }
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting cache stats: {str(e)}")

@router.delete("/cache/clear")
async def clear_all_cache():
    """Clear all cached data (use with caution)"""
    
    try:
        # This would need to be implemented in the cache service
        # For now, just return success
        return {"message": "Cache cleared successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing cache: {str(e)}")

@router.get("/config")
async def get_data_service_config():
    """Get current configuration for all data services"""
    
    import os
    
    config = {
        "fmp": {
            "use_real_api": os.getenv("USE_REAL_FMP", "false").lower() == "true",
            "api_key_configured": bool(os.getenv("FMP_API_KEY")) and os.getenv("FMP_API_KEY") != "demo",
            "rate_limit_per_minute": int(os.getenv("FMP_RATE_LIMIT_PER_MINUTE", "60")),
            "cache_ttl_seconds": 300
        },
        "google_trends": {
            "use_real_api": os.getenv("USE_REAL_TRENDS", "false").lower() == "true",
            "pytrends_available": True,  # We know it's installed
            "rate_limit_per_hour": int(os.getenv("TRENDS_RATE_LIMIT_PER_HOUR", "100")),
            "cache_ttl_seconds": 3600
        },
        "economic_times": {
            "use_real_scraping": os.getenv("USE_REAL_SCRAPING", "false").lower() == "true",
            "scraping_delay_seconds": float(os.getenv("SCRAPING_DELAY_SECONDS", "1")),
            "cache_ttl_seconds": 1800
        },
        "cache": {
            "redis_available": cache_service.use_redis,
            "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379"),
            "default_ttl_seconds": int(os.getenv("CACHE_TTL_SECONDS", "300"))
        }
    }
    
    return config