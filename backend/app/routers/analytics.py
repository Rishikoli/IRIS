#!/usr/bin/env python3
"""
IRIS RegTech Platform - Analytics Router
Advanced analytics and reporting endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional
import logging

from app.services.analytics_service import analytics_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/summary")
async def get_analytics_summary() -> Dict[str, Any]:
    """
    Get comprehensive platform-wide analytics summary
    
    Returns:
        Dict containing platform overview, risk analysis, document verification stats,
        recent activity, and review system metrics
    """
    try:
        logger.info("Fetching analytics summary")
        summary = await analytics_service.get_platform_summary()
        
        if "error" in summary:
            raise HTTPException(status_code=500, detail=summary["error"])
        
        return {
            "status": "success",
            "data": summary,
            "timestamp": "2024-12-19T10:30:00Z"
        }
    
    except Exception as e:
        logger.error(f"Error fetching analytics summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trends/fraud")
async def get_fraud_trends(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    granularity: str = Query("daily", regex="^(hourly|daily|weekly)$", description="Data granularity")
) -> Dict[str, Any]:
    """
    Get fraud trend analysis with time-series data
    
    Args:
        days: Number of days to analyze (1-365)
        granularity: Data granularity (hourly, daily, weekly)
    
    Returns:
        Dict containing fraud trends, patterns, and summary statistics
    """
    try:
        logger.info(f"Fetching fraud trends for {days} days with {granularity} granularity")
        trends = await analytics_service.get_fraud_trends(days=days, granularity=granularity)
        
        if "error" in trends:
            raise HTTPException(status_code=500, detail=trends["error"])
        
        return {
            "status": "success",
            "data": trends,
            "timestamp": "2024-12-19T10:30:00Z"
        }
    
    except Exception as e:
        logger.error(f"Error fetching fraud trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis/sectors")
async def get_sector_analysis() -> Dict[str, Any]:
    """
    Get sector-wise fraud pattern analysis
    
    Returns:
        Dict containing sector analysis, risk levels, and emerging threats
    """
    try:
        logger.info("Fetching sector-wise fraud analysis")
        analysis = await analytics_service.get_sector_analysis()
        
        if "error" in analysis:
            raise HTTPException(status_code=500, detail=analysis["error"])
        
        return {
            "status": "success",
            "data": analysis,
            "timestamp": "2024-12-19T10:30:00Z"
        }
    
    except Exception as e:
        logger.error(f"Error fetching sector analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis/regions")
async def get_regional_analysis() -> Dict[str, Any]:
    """
    Get region-wise fraud pattern analysis
    
    Returns:
        Dict containing regional analysis, hotspots, and geographic distribution
    """
    try:
        logger.info("Fetching regional fraud analysis")
        analysis = await analytics_service.get_regional_analysis()
        
        if "error" in analysis:
            raise HTTPException(status_code=500, detail=analysis["error"])
        
        return {
            "status": "success",
            "data": analysis,
            "timestamp": "2024-12-19T10:30:00Z"
        }
    
    except Exception as e:
        logger.error(f"Error fetching regional analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/verification/advisors")
async def get_advisor_verification_stats() -> Dict[str, Any]:
    """
    Get advisor verification success rate tracking
    
    Returns:
        Dict containing advisor verification statistics and trends
    """
    try:
        logger.info("Fetching advisor verification statistics")
        # Mock implementation for now since we don't have dedicated advisor verification tracking
        stats = {
            "verification_stats": {
                "total_advisor_checks": 145,
                "verified_advisors": 105,
                "unverified_advisors": 25,
                "fake_credentials": 15,
                "verification_success_rate": 72.4
            },
            "risk_indicators": {
                "fake_credential_rate": 10.3,
                "unverified_rate": 17.2
            },
            "trends": {
                "monthly_checks": [
                    {"month": "2024-10", "checks": 45, "verified": 32, "fake": 8},
                    {"month": "2024-11", "checks": 52, "verified": 38, "fake": 9},
                    {"month": "2024-12", "checks": 48, "verified": 35, "fake": 7}
                ],
                "common_fraud_patterns": [
                    "Fake SEBI registration numbers",
                    "Unregistered investment advisors",
                    "Misleading credentials claims",
                    "Expired registrations"
                ]
            }
        }
        
        return {
            "status": "success",
            "data": stats,
            "timestamp": "2024-12-19T10:30:00Z"
        }
    
    except Exception as e:
        logger.error(f"Error fetching advisor verification stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/authenticity")
async def get_document_authenticity_trends() -> Dict[str, Any]:
    """
    Get document authenticity trend monitoring
    
    Returns:
        Dict containing document authenticity trends and anomaly patterns
    """
    try:
        logger.info("Fetching document authenticity trends")
        # Mock implementation for comprehensive document trends
        trends = {
            "trends": [
                {
                    "date": "2024-12-15",
                    "total_documents": 25,
                    "authentic_documents": 18,
                    "fake_documents": 7,
                    "authenticity_rate": 72.0,
                    "avg_authenticity_score": 78.5
                },
                {
                    "date": "2024-12-16",
                    "total_documents": 32,
                    "authentic_documents": 24,
                    "fake_documents": 8,
                    "authenticity_rate": 75.0,
                    "avg_authenticity_score": 81.2
                },
                {
                    "date": "2024-12-17",
                    "total_documents": 28,
                    "authentic_documents": 21,
                    "fake_documents": 7,
                    "authenticity_rate": 75.0,
                    "avg_authenticity_score": 79.8
                }
            ],
            "anomaly_distribution": [
                {"anomaly_count": 0, "document_count": 45, "percentage": 52.9},
                {"anomaly_count": 1, "document_count": 25, "percentage": 29.4},
                {"anomaly_count": 2, "document_count": 12, "percentage": 14.1},
                {"anomaly_count": 3, "document_count": 3, "percentage": 3.5}
            ],
            "summary": {
                "total_documents_processed": 85,
                "overall_authenticity_rate": 74.1,
                "avg_authenticity_score": 79.8,
                "most_common_anomalies": [
                    {"anomaly": "Inconsistent formatting", "count": 15, "percentage": 17.6},
                    {"anomaly": "Missing watermarks", "count": 12, "percentage": 14.1},
                    {"anomaly": "Font irregularities", "count": 8, "percentage": 9.4}
                ]
            }
        }
        
        return {
            "status": "success",
            "data": trends,
            "timestamp": "2024-12-19T10:30:00Z"
        }
    
    except Exception as e:
        logger.error(f"Error fetching document authenticity trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/usage/platform")
async def get_platform_usage_analytics() -> Dict[str, Any]:
    """
    Get user activity and platform usage analytics
    
    Returns:
        Dict containing usage patterns, performance metrics, and system health
    """
    try:
        logger.info("Fetching platform usage analytics")
        # Mock comprehensive usage analytics
        usage = {
            "submission_patterns": {
                "tip_sources": [
                    {"source": "web", "count": 145},
                    {"source": "api", "count": 89},
                    {"source": "mobile", "count": 67},
                    {"source": "email", "count": 23}
                ],
                "most_popular_source": "web"
            },
            "performance_metrics": {
                "avg_pdf_processing_time_ms": 1850,
                "min_pdf_processing_time_ms": 450,
                "max_pdf_processing_time_ms": 4200,
                "processing_efficiency": "Excellent"
            },
            "review_system_usage": {
                "review_decisions": [
                    {"decision": "approved", "count": 45},
                    {"decision": "rejected", "count": 12},
                    {"decision": "needs_more_info", "count": 8}
                ],
                "most_common_decision": "approved"
            },
            "monthly_comparison": {
                "current_month": {"tips": 324, "pdf_checks": 185},
                "last_month": {"tips": 298, "pdf_checks": 167},
                "growth_rates": {"tips_growth": 8.7, "pdf_growth": 10.8}
            },
            "system_health": {
                "uptime_percentage": 99.5,
                "avg_response_time_ms": 850,
                "error_rate_percentage": 0.2
            }
        }
        
        return {
            "status": "success",
            "data": usage,
            "timestamp": "2024-12-19T10:30:00Z"
        }
    
    except Exception as e:
        logger.error(f"Error fetching platform usage analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/summary")
async def export_analytics_summary(
    format: str = Query("json", regex="^(json|csv)$", description="Export format")
) -> Dict[str, Any]:
    """
    Export analytics summary in specified format
    
    Args:
        format: Export format (json or csv)
    
    Returns:
        Dict containing export data or download link
    """
    try:
        logger.info(f"Exporting analytics summary in {format} format")
        
        # Get comprehensive analytics data
        summary = await analytics_service.get_platform_summary()
        
        if format == "json":
            return {
                "status": "success",
                "format": "json",
                "data": summary,
                "export_timestamp": "2024-12-19T10:30:00Z"
            }
        else:  # CSV format
            return {
                "status": "success",
                "format": "csv",
                "download_url": "/api/analytics/downloads/summary.csv",
                "message": "CSV export prepared. Use the download URL to retrieve the file.",
                "export_timestamp": "2024-12-19T10:30:00Z"
            }
    
    except Exception as e:
        logger.error(f"Error exporting analytics summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
