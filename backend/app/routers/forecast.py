from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from app.database import get_db
from app.services.forecasting_service import ForecastingService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["forecast"])

@router.get("/forecast")
async def get_forecast(
    dimension: str = Query(..., description="Dimension to forecast: 'sector' or 'region'"),
    period: Optional[str] = Query(None, description="Period in YYYY-MM format, defaults to next month"),
    regenerate: bool = Query(False, description="Force regenerate forecast"),
    db: Session = Depends(get_db)
):
    """
    Get AI-powered fraud risk forecasts with explainability
    """
    try:
        # Validate dimension
        if dimension not in ["sector", "region"]:
            raise HTTPException(status_code=400, detail="Dimension must be 'sector' or 'region'")
        
        # Default to next month if period not specified
        if not period:
            next_month = datetime.now() + timedelta(days=30)
            period = next_month.strftime("%Y-%m")
        
        # Validate period format
        try:
            datetime.strptime(period, "%Y-%m")
        except ValueError:
            raise HTTPException(status_code=400, detail="Period must be in YYYY-MM format")
        
        forecasting_service = ForecastingService(db)
        
        # Check if we need to regenerate or if forecasts exist
        if regenerate:
            forecasts = await forecasting_service.generate_forecast(dimension, period)
        else:
            # Try to get existing forecasts first
            forecasts = forecasting_service.get_stored_forecasts(dimension, period)
            
            # If no forecasts exist, generate them
            if not forecasts:
                forecasts = await forecasting_service.generate_forecast(dimension, period)
        
        # Get accuracy metrics
        accuracy_metrics = forecasting_service.get_forecast_accuracy_metrics(dimension)
        
        return {
            "dimension": dimension,
            "period": period,
            "forecasts": forecasts,
            "accuracy_metrics": accuracy_metrics,
            "generated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting forecast: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/forecast/accuracy")
async def get_forecast_accuracy(
    dimension: str = Query(..., description="Dimension: 'sector' or 'region'"),
    db: Session = Depends(get_db)
):
    """
    Get historical forecast accuracy metrics
    """
    try:
        if dimension not in ["sector", "region"]:
            raise HTTPException(status_code=400, detail="Dimension must be 'sector' or 'region'")
        
        forecasting_service = ForecastingService(db)
        accuracy_metrics = forecasting_service.get_forecast_accuracy_metrics(dimension)
        
        return {
            "dimension": dimension,
            "accuracy_metrics": accuracy_metrics
        }
        
    except Exception as e:
        logger.error(f"Error getting forecast accuracy: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/forecast/compare")
async def compare_forecasts(
    dimension: str = Query(..., description="Dimension: 'sector' or 'region'"),
    periods: List[str] = Query(..., description="List of periods to compare in YYYY-MM format"),
    db: Session = Depends(get_db)
):
    """
    Compare forecasts across different time periods
    """
    try:
        if dimension not in ["sector", "region"]:
            raise HTTPException(status_code=400, detail="Dimension must be 'sector' or 'region'")
        
        # Validate periods
        for period in periods:
            try:
                datetime.strptime(period, "%Y-%m")
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid period format: {period}")
        
        forecasting_service = ForecastingService(db)
        
        comparison_data = {}
        for period in periods:
            forecasts = forecasting_service.get_stored_forecasts(dimension, period)
            comparison_data[period] = forecasts
        
        return {
            "dimension": dimension,
            "periods": periods,
            "comparison_data": comparison_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing forecasts: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")