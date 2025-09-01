"""
Multi-Source Data Integration API Endpoints
Provides endpoints for FMP, Google Trends, Economic Times data and correlations
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timedelta

from app.database import get_db
from app.services.fmp_service import FMPIntegrationService
from app.services.google_trends_service import GoogleTrendsService
from app.services.economic_times_service import EconomicTimesScrapingService
from app.services.data_aggregation_service import DataAggregationService
from app.models import DataIndicator, CrossSourceCorrelation

router = APIRouter()

# Response Models
class DataIndicatorResponse(BaseModel):
    id: str
    sector: Optional[str]
    region: Optional[str]
    indicator_type: str
    source: str
    relevance_score: int
    summary: str
    details: Dict[str, Any]
    active: bool
    created_at: datetime

class MultiSourceOverlayResponse(BaseModel):
    indicators: List[DataIndicatorResponse]
    summary: Dict[str, Any]
    last_updated: datetime
    sources_status: Dict[str, str]

class CorrelationResponse(BaseModel):
    correlation_type: str
    source_1: str
    source_2: str
    correlation_strength: float
    fraud_implication: str
    analysis_summary: str
    created_at: datetime

class DataSourceToggleRequest(BaseModel):
    fmp_enabled: bool = True
    google_trends_enabled: bool = True
    economic_times_enabled: bool = True

# Initialize services
fmp_service = FMPIntegrationService()
trends_service = GoogleTrendsService()
et_service = EconomicTimesScrapingService()
aggregation_service = DataAggregationService()

@router.get("/data/indicators", response_model=MultiSourceOverlayResponse)
async def get_multi_source_indicators(
    sector: Optional[str] = Query(None, description="Filter by sector"),
    region: Optional[str] = Query(None, description="Filter by region"),
    source: Optional[str] = Query(None, description="Filter by data source"),
    min_relevance: int = Query(40, description="Minimum relevance score"),
    db: Session = Depends(get_db)
):
    """Get multi-source data indicators for heatmap overlay"""
    try:
        # Query database for active indicators
        query = db.query(DataIndicator).filter(
            DataIndicator.active == True,
            DataIndicator.relevance_score >= min_relevance,
            DataIndicator.expires_at > datetime.now()
        )
        
        if sector:
            query = query.filter(DataIndicator.heatmap_sector == sector)
        if region:
            query = query.filter(DataIndicator.heatmap_region == region)
        if source:
            query = query.filter(DataIndicator.source == source)
        
        indicators = query.order_by(DataIndicator.relevance_score.desc()).all()
        
        # Convert to response format
        indicator_responses = []
        for indicator in indicators:
            indicator_responses.append(DataIndicatorResponse(
                id=indicator.id,
                sector=indicator.heatmap_sector,
                region=indicator.heatmap_region,
                indicator_type=indicator.indicator_type,
                source=indicator.source,
                relevance_score=indicator.relevance_score,
                summary=indicator.summary,
                details=indicator.details,
                active=indicator.active,
                created_at=indicator.created_at
            ))
        
        # Generate summary statistics
        total_indicators = len(indicator_responses)
        high_relevance_count = len([i for i in indicator_responses if i.relevance_score > 70])
        sources_active = list(set([i.source for i in indicator_responses]))
        
        summary = {
            "total_indicators": total_indicators,
            "high_relevance_count": high_relevance_count,
            "sources_active": sources_active,
            "avg_relevance_score": sum(i.relevance_score for i in indicator_responses) / max(1, total_indicators)
        }
        
        # Check sources status
        sources_status = {
            "fmp": "active" if "fmp" in sources_active else "inactive",
            "google_trends": "active" if "google_trends" in sources_active else "inactive",
            "economic_times": "active" if "economic_times" in sources_active else "inactive"
        }
        
        return MultiSourceOverlayResponse(
            indicators=indicator_responses,
            summary=summary,
            last_updated=datetime.now(),
            sources_status=sources_status
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching multi-source indicators: {str(e)}")

@router.post("/data/refresh")
async def refresh_multi_source_data(
    background_tasks: BackgroundTasks,
    sources: DataSourceToggleRequest = DataSourceToggleRequest(),
    db: Session = Depends(get_db)
):
    """Refresh data from all enabled sources"""
    try:
        # Add background task to refresh data
        background_tasks.add_task(
            _refresh_data_background,
            db,
            sources.fmp_enabled,
            sources.google_trends_enabled,
            sources.economic_times_enabled
        )
        
        return {
            "message": "Data refresh initiated",
            "sources_enabled": {
                "fmp": sources.fmp_enabled,
                "google_trends": sources.google_trends_enabled,
                "economic_times": sources.economic_times_enabled
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initiating data refresh: {str(e)}")

@router.get("/fmp/market-data")
async def get_fmp_market_data(
    symbols: Optional[str] = Query(None, description="Comma-separated stock symbols")
):
    """Get real-time market data from FMP API"""
    try:
        symbol_list = symbols.split(",") if symbols else None
        market_data = await fmp_service.fetch_market_data(symbol_list)
        
        return {
            "data": [data.dict() for data in market_data],
            "timestamp": datetime.now().isoformat(),
            "source": "fmp"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching FMP market data: {str(e)}")

@router.get("/fmp/stock-alerts")
async def get_fmp_stock_alerts():
    """Get stock alerts from FMP data analysis"""
    try:
        # Fetch market data and analyze for alerts
        market_data = await fmp_service.fetch_market_data()
        alerts = await fmp_service.detect_unusual_activity(market_data)
        
        return {
            "alerts": [alert.dict() for alert in alerts],
            "total_alerts": len(alerts),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stock alerts: {str(e)}")

@router.get("/trends/fraud-keywords")
async def get_fraud_keyword_trends(
    regions: Optional[str] = Query(None, description="Comma-separated regions"),
    timeframe: str = Query("7d", description="Timeframe for trends")
):
    """Get Google Trends data for fraud-related keywords"""
    try:
        region_list = regions.split(",") if regions else None
        trends_data = await trends_service.fetch_fraud_trends(region_list, timeframe)
        
        return {
            "trends": [trend.dict() for trend in trends_data],
            "total_trends": len(trends_data),
            "timeframe": timeframe,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching fraud keyword trends: {str(e)}")

@router.get("/trends/regional-spikes")
async def get_regional_spikes():
    """Get regions with unusual spikes in fraud-related searches"""
    try:
        # Fetch trends data and analyze for spikes
        trends_data = await trends_service.fetch_fraud_trends()
        spikes = await trends_service.analyze_search_spikes(trends_data)
        
        return {
            "spikes": [spike.dict() for spike in spikes],
            "total_spikes": len(spikes),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching regional spikes: {str(e)}")

@router.get("/economic-times/latest-news")
async def get_economic_times_news(
    categories: Optional[str] = Query(None, description="Comma-separated categories")
):
    """Get latest financial news from Economic Times"""
    try:
        category_list = categories.split(",") if categories else None
        articles = await et_service.scrape_latest_news(category_list)
        
        return {
            "articles": [article.dict() for article in articles],
            "total_articles": len(articles),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching Economic Times news: {str(e)}")

@router.get("/economic-times/regulatory-updates")
async def get_regulatory_updates():
    """Get regulatory updates from Economic Times"""
    try:
        updates = await et_service.monitor_regulatory_updates()
        
        return {
            "updates": [update.dict() for update in updates],
            "total_updates": len(updates),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching regulatory updates: {str(e)}")

@router.get("/data/correlations", response_model=List[CorrelationResponse])
async def get_cross_source_correlations(
    min_strength: float = Query(50.0, description="Minimum correlation strength"),
    limit: int = Query(10, description="Maximum number of correlations to return"),
    db: Session = Depends(get_db)
):
    """Get cross-source data correlations"""
    try:
        # Query database for correlations
        correlations = db.query(CrossSourceCorrelation).filter(
            CrossSourceCorrelation.correlation_strength >= min_strength
        ).order_by(CrossSourceCorrelation.correlation_strength.desc()).limit(limit).all()
        
        # Convert to response format
        correlation_responses = []
        for corr in correlations:
            correlation_responses.append(CorrelationResponse(
                correlation_type=corr.correlation_type,
                source_1=corr.source_1,
                source_2=corr.source_2,
                correlation_strength=corr.correlation_strength / 100.0,  # Convert back to 0-1 scale
                fraud_implication=corr.fraud_implication,
                analysis_summary=corr.analysis_summary,
                created_at=corr.created_at
            ))
        
        return correlation_responses
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching correlations: {str(e)}")

@router.get("/data/consolidated-modal/{sector}/{region}")
async def get_consolidated_data_modal(
    sector: str,
    region: str,
    db: Session = Depends(get_db)
):
    """Get consolidated data modal with fraud relevance details from all sources"""
    try:
        # Get indicators for the specific sector/region
        indicators = db.query(DataIndicator).filter(
            DataIndicator.heatmap_sector == sector,
            DataIndicator.heatmap_region == region,
            DataIndicator.active == True,
            DataIndicator.expires_at > datetime.now()
        ).order_by(DataIndicator.relevance_score.desc()).all()
        
        # Group by source
        sources_data = {}
        for indicator in indicators:
            if indicator.source not in sources_data:
                sources_data[indicator.source] = []
            sources_data[indicator.source].append({
                "id": indicator.id,
                "type": indicator.indicator_type,
                "relevance_score": indicator.relevance_score,
                "summary": indicator.summary,
                "details": indicator.details,
                "created_at": indicator.created_at.isoformat()
            })
        
        # Calculate overall risk assessment
        total_indicators = len(indicators)
        avg_relevance = sum(i.relevance_score for i in indicators) / max(1, total_indicators)
        
        if avg_relevance > 70:
            risk_level = "high"
        elif avg_relevance > 40:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "sector": sector,
            "region": region,
            "risk_level": risk_level,
            "average_relevance": round(avg_relevance, 1),
            "total_indicators": total_indicators,
            "sources_data": sources_data,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching consolidated modal data: {str(e)}")

async def _refresh_data_background(
    db: Session,
    fmp_enabled: bool,
    trends_enabled: bool,
    et_enabled: bool
):
    """Background task to refresh multi-source data"""
    try:
        # Deactivate old indicators
        db.query(DataIndicator).filter(
            DataIndicator.expires_at <= datetime.now()
        ).update({"active": False})
        
        # Generate new indicators
        indicators = await aggregation_service.generate_consolidated_indicators([])
        
        # Filter based on enabled sources
        filtered_indicators = []
        for indicator in indicators:
            if ((indicator.source == "fmp" and fmp_enabled) or
                (indicator.source == "google_trends" and trends_enabled) or
                (indicator.source == "economic_times" and et_enabled)):
                filtered_indicators.append(indicator)
        
        # Store in database
        await aggregation_service.store_indicators_in_db(db, filtered_indicators)
        
        print(f"Refreshed {len(filtered_indicators)} indicators from enabled sources")
        
    except Exception as e:
        print(f"Error in background data refresh: {e}")
        db.rollback()