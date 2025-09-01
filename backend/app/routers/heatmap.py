from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import date, datetime
from app.database import get_db
from app import crud
from app.exceptions import (
    ValidationException,
    ExternalServiceException,
    ErrorDetail
)

router = APIRouter()

class HeatmapBucketResponse(BaseModel):
    dimension: str
    key: str
    from_date: str
    to_date: str
    total_count: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    risk_score: float
    last_updated: str

class HeatmapStatsResponse(BaseModel):
    total_cases: int
    high_risk_cases: int
    medium_risk_cases: int
    low_risk_cases: int
    average_risk_score: float
    trend_direction: str  # "up", "down", "stable"

class FraudHeatmapResponse(BaseModel):
    data: List[HeatmapBucketResponse]
    stats: HeatmapStatsResponse
    filters: dict

@router.get("/fraud-heatmap", response_model=FraudHeatmapResponse)
async def get_fraud_heatmap(
    dimension: str = Query(..., description="Dimension to aggregate by", pattern="^(sector|region)$"),
    period: str = Query("weekly", description="Time period for aggregation", pattern="^(daily|weekly|monthly)$"),
    from_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)", pattern="^\\d{4}-\\d{2}-\\d{2}$"),
    to_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)", pattern="^\\d{4}-\\d{2}-\\d{2}$"),
    db: Session = Depends(get_db)
):
    """
    Get fraud activity heatmap data aggregated by sector or region.
    
    - **dimension**: Either 'sector' or 'region'
    - **period**: Aggregation period - 'daily', 'weekly', or 'monthly'
    - **from_date**: Optional start date filter (YYYY-MM-DD)
    - **to_date**: Optional end date filter (YYYY-MM-DD)
    """
    
    # Parse date parameters
    parsed_from_date = None
    parsed_to_date = None
    
    try:
        if from_date:
            parsed_from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
        if to_date:
            parsed_to_date = datetime.strptime(to_date, "%Y-%m-%d").date()
    except ValueError:
        raise ValidationException(
            "Invalid date format",
            details=[ErrorDetail(
                code="invalid_date_format",
                message="Date must be in YYYY-MM-DD format",
                field="date"
            )]
        )
    
    # Validate date range
    if parsed_from_date and parsed_to_date and parsed_from_date > parsed_to_date:
        raise ValidationException(
            "Invalid date range",
            details=[ErrorDetail(
                code="invalid_date_range",
                message="from_date must be before to_date",
                field="date_range"
            )]
        )
    
    try:
        # Get aggregated heatmap data
        heatmap_data = crud.aggregate_heatmap_data(
            db=db,
            dimension=dimension,
            period=period,
            from_date=parsed_from_date,
            to_date=parsed_to_date
        )
        
        # Calculate overall statistics
        total_cases = sum(item["total_count"] for item in heatmap_data)
        high_risk_cases = sum(item["high_risk_count"] for item in heatmap_data)
        medium_risk_cases = sum(item["medium_risk_count"] for item in heatmap_data)
        low_risk_cases = sum(item["low_risk_count"] for item in heatmap_data)
        
        # Calculate average risk score
        if heatmap_data:
            average_risk_score = sum(item["risk_score"] for item in heatmap_data) / len(heatmap_data)
        else:
            average_risk_score = 0.0
        
        # Simple trend calculation (for demo purposes)
        # In production, this would compare with previous period
        if average_risk_score > 70:
            trend_direction = "up"
        elif average_risk_score < 30:
            trend_direction = "down"
        else:
            trend_direction = "stable"
        
        # Prepare response
        response_data = [
            HeatmapBucketResponse(**item) for item in heatmap_data
        ]
        
        stats = HeatmapStatsResponse(
            total_cases=total_cases,
            high_risk_cases=high_risk_cases,
            medium_risk_cases=medium_risk_cases,
            low_risk_cases=low_risk_cases,
            average_risk_score=round(average_risk_score, 2),
            trend_direction=trend_direction
        )
        
        filters_applied = {
            "dimension": dimension,
            "period": period,
            "from_date": from_date,
            "to_date": to_date
        }
        
        return FraudHeatmapResponse(
            data=response_data,
            stats=stats,
            filters=filters_applied
        )
        
    except ValidationException:
        raise
    except ValueError as e:
        raise ValidationException(str(e))
    except Exception as e:
        raise ExternalServiceException("database", f"Failed to retrieve heatmap data: {str(e)}")

@router.get("/heatmap-keys/{dimension}")
async def get_heatmap_keys(dimension: str):
    """Get available keys for a specific dimension"""
    if dimension == "sector":
        return {
            "keys": ["Technology", "Banking", "Pharma", "Energy", "FMCG", "Auto", "Telecom", "Real Estate"]
        }
    elif dimension == "region":
        return {
            "keys": ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune", "Ahmedabad"]
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid dimension. Must be 'sector' or 'region'")

@router.post("/populate-sample-heatmap-data")
async def populate_sample_heatmap_data(db: Session = Depends(get_db)):
    """Populate sample heatmap data for demonstration purposes"""
    
    try:
        # Generate real-time sample fraud cases
        sample_cases = crud.generate_realtime_fraud_cases(db)
        
        # This will trigger the aggregation which creates sample data
        # based on existing assessments
        sample_data = crud.aggregate_heatmap_data(
            db=db,
            dimension="sector",
            period="weekly"
        )
        
        region_data = crud.aggregate_heatmap_data(
            db=db,
            dimension="region",
            period="weekly"
        )
        
        return {
            "message": "Real-time heatmap data populated successfully",
            "cases_generated": len(sample_cases),
            "sector_buckets": len(sample_data),
            "region_buckets": len(region_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error populating sample data: {str(e)}")

@router.post("/generate-realtime-data")
async def generate_realtime_data(db: Session = Depends(get_db)):
    """Generate new real-time fraud cases for live demonstration"""
    
    try:
        # Generate new fraud cases
        new_cases = crud.generate_realtime_fraud_cases(db, count=5)
        
        return {
            "message": "New real-time fraud cases generated",
            "cases_generated": len(new_cases),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating real-time data: {str(e)}")

@router.get("/heatmap-drill-down/{dimension}/{key}")
async def get_heatmap_drill_down(
    dimension: str,
    key: str,
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get detailed drill-down data for a specific heatmap cell"""
    
    # Parse date parameters
    parsed_from_date = None
    parsed_to_date = None
    
    try:
        if from_date:
            parsed_from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
        if to_date:
            parsed_to_date = datetime.strptime(to_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    try:
        drill_down_data = crud.get_heatmap_drill_down_data(
            db=db,
            dimension=dimension,
            key=key,
            from_date=parsed_from_date,
            to_date=parsed_to_date
        )
        
        return drill_down_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting drill-down data: {str(e)}")