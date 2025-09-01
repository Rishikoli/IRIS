import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import statistics
import math

from app.models import Forecast, HeatmapBucket, Assessment, Tip
from app.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class ForecastingService:
    def __init__(self, db: Session):
        self.db = db
        self.gemini_service = GeminiService()
    
    async def generate_forecast(self, dimension: str, period: str) -> List[Dict[str, Any]]:
        """Generate AI-powered risk forecasts with explainability"""
        try:
            # Get historical data for the dimension
            historical_data = self._get_historical_data(dimension)
            
            forecasts = []
            for key, data in historical_data.items():
                # Calculate time-series features
                features = self._calculate_trend_features(data)
                
                # Generate base forecast using trend analysis
                base_score = self._calculate_base_forecast(features)
                
                # Calculate confidence intervals
                confidence_min, confidence_max = self._calculate_confidence_intervals(base_score, features)
                
                # Generate AI rationale and contributing factors
                rationale, factors = await self._generate_ai_explanation(key, dimension, features, base_score)
                
                # Store forecast in database
                forecast = Forecast(
                    period=period,
                    dimension=dimension,
                    key=key,
                    risk_score=base_score,
                    confidence_min=confidence_min,
                    confidence_max=confidence_max,
                    rationale=rationale,
                    contributing_factors=factors,
                    features=features
                )
                
                self.db.add(forecast)
                
                forecasts.append({
                    "key": key,
                    "risk_score": base_score,
                    "confidence_interval": [confidence_min, confidence_max],
                    "rationale": rationale,
                    "contributing_factors": factors,
                    "features": features
                })
            
            self.db.commit()
            return forecasts
            
        except Exception as e:
            logger.error(f"Error generating forecast: {str(e)}")
            self.db.rollback()
            raise
    
    def _get_historical_data(self, dimension: str) -> Dict[str, List[Dict]]:
        """Get historical heatmap data for trend analysis"""
        # Get data from last 6 months
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=180)
        
        buckets = self.db.query(HeatmapBucket).filter(
            HeatmapBucket.dimension == dimension,
            HeatmapBucket.from_date >= start_date,
            HeatmapBucket.to_date <= end_date
        ).order_by(HeatmapBucket.from_date).all()
        
        # Group by key
        historical_data = {}
        for bucket in buckets:
            if bucket.key not in historical_data:
                historical_data[bucket.key] = []
            
            historical_data[bucket.key].append({
                "date": bucket.from_date,
                "total_count": bucket.total_count,
                "high_risk_count": bucket.high_risk_count,
                "medium_risk_count": bucket.medium_risk_count,
                "low_risk_count": bucket.low_risk_count,
                "risk_ratio": bucket.high_risk_count / max(bucket.total_count, 1)
            })
        
        return historical_data
    
    def _calculate_trend_features(self, data: List[Dict]) -> Dict[str, Any]:
        """Calculate time-series features for forecasting"""
        if not data:
            return {}
        
        # Sort by date
        data = sorted(data, key=lambda x: x["date"])
        
        # Extract time series
        risk_ratios = [d["risk_ratio"] for d in data]
        total_counts = [d["total_count"] for d in data]
        
        features = {
            "data_points": len(data),
            "avg_risk_ratio": statistics.mean(risk_ratios) if risk_ratios else 0,
            "risk_ratio_trend": self._calculate_trend(risk_ratios),
            "volatility": statistics.stdev(risk_ratios) if len(risk_ratios) > 1 else 0,
            "recent_avg": statistics.mean(risk_ratios[-4:]) if len(risk_ratios) >= 4 else statistics.mean(risk_ratios),
            "volume_trend": self._calculate_trend(total_counts),
            "peak_risk_ratio": max(risk_ratios) if risk_ratios else 0,
            "recent_spike": self._detect_recent_spike(risk_ratios)
        }
        
        return features
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate linear trend slope"""
        if len(values) < 2:
            return 0
        
        n = len(values)
        x = list(range(n))
        
        # Calculate linear regression slope
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(values)
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        return numerator / denominator if denominator != 0 else 0
    
    def _detect_recent_spike(self, values: List[float]) -> bool:
        """Detect if there's a recent spike in risk ratios"""
        if len(values) < 4:
            return False
        
        recent = values[-2:]  # Last 2 data points
        baseline = values[:-2]  # All but last 2
        
        if not baseline:
            return False
        
        baseline_avg = statistics.mean(baseline)
        recent_avg = statistics.mean(recent)
        
        # Spike if recent average is 50% higher than baseline
        return recent_avg > baseline_avg * 1.5
    
    def _calculate_base_forecast(self, features: Dict[str, Any]) -> int:
        """Calculate base forecast score using trend analysis"""
        if not features:
            return 50  # Default medium risk
        
        base_score = features.get("recent_avg", 0.5) * 100
        
        # Adjust based on trend
        trend_adjustment = features.get("risk_ratio_trend", 0) * 20
        base_score += trend_adjustment
        
        # Adjust for volatility (higher volatility = higher risk)
        volatility_adjustment = features.get("volatility", 0) * 15
        base_score += volatility_adjustment
        
        # Adjust for recent spikes
        if features.get("recent_spike", False):
            base_score += 15
        
        # Clamp to 0-100 range
        return max(0, min(100, int(base_score)))
    
    def _calculate_confidence_intervals(self, base_score: int, features: Dict[str, Any]) -> Tuple[int, int]:
        """Calculate confidence intervals for forecasts"""
        # Base confidence range
        confidence_range = 15
        
        # Adjust based on data quality
        data_points = features.get("data_points", 0)
        if data_points < 4:
            confidence_range += 10  # Less confident with less data
        
        # Adjust based on volatility
        volatility = features.get("volatility", 0)
        confidence_range += int(volatility * 20)
        
        # Calculate bounds
        confidence_min = max(0, base_score - confidence_range)
        confidence_max = min(100, base_score + confidence_range)
        
        return confidence_min, confidence_max
    
    async def _generate_ai_explanation(self, key: str, dimension: str, features: Dict[str, Any], score: int) -> Tuple[str, List[Dict]]:
        """Generate AI rationale and contributing factors"""
        try:
            prompt = f"""
            Analyze the fraud risk forecast for {dimension} "{key}" with a predicted risk score of {score}/100.
            
            Historical data features:
            - Average risk ratio: {features.get('avg_risk_ratio', 0):.2f}
            - Risk trend: {features.get('risk_ratio_trend', 0):.3f}
            - Volatility: {features.get('volatility', 0):.2f}
            - Recent spike detected: {features.get('recent_spike', False)}
            - Data points available: {features.get('data_points', 0)}
            
            Provide:
            1. A concise rationale (2-3 sentences) explaining why this risk level is predicted
            2. Top 3 contributing factors with weights and explanations
            
            Format as JSON:
            {{
                "rationale": "explanation text",
                "factors": [
                    {{"factor": "factor name", "weight": 0.4, "explanation": "why this matters"}},
                    {{"factor": "factor name", "weight": 0.3, "explanation": "why this matters"}},
                    {{"factor": "factor name", "weight": 0.3, "explanation": "why this matters"}}
                ]
            }}
            """
            
            response = await self.gemini_service.analyze_text(prompt)
            
            # Parse JSON response
            try:
                parsed = json.loads(response)
                rationale = parsed.get("rationale", f"Risk level {score}/100 predicted based on historical trends.")
                factors = parsed.get("factors", [])
            except (json.JSONDecodeError, TypeError):
                # Fallback if JSON parsing fails or response is not a string
                rationale = f"Risk level {score}/100 predicted based on historical fraud patterns and trend analysis."
                factors = self._generate_fallback_factors(features)
            
            return rationale, factors
            
        except Exception as e:
            logger.error(f"Error generating AI explanation: {str(e)}")
            # Fallback explanation
            rationale = f"Risk level {score}/100 predicted based on historical fraud patterns and trend analysis."
            factors = self._generate_fallback_factors(features)
            return rationale, factors
    
    def _generate_fallback_factors(self, features: Dict[str, Any]) -> List[Dict]:
        """Generate fallback contributing factors"""
        factors = []
        
        # Historical trend factor
        trend = features.get("risk_ratio_trend", 0)
        if trend > 0:
            factors.append({
                "factor": "Increasing Trend",
                "weight": 0.4,
                "explanation": "Historical data shows an upward trend in fraud activity"
            })
        elif trend < 0:
            factors.append({
                "factor": "Decreasing Trend", 
                "weight": 0.4,
                "explanation": "Historical data shows a downward trend in fraud activity"
            })
        else:
            factors.append({
                "factor": "Stable Pattern",
                "weight": 0.3,
                "explanation": "Fraud activity has remained relatively stable"
            })
        
        # Volatility factor
        volatility = features.get("volatility", 0)
        if volatility > 0.2:
            factors.append({
                "factor": "High Volatility",
                "weight": 0.3,
                "explanation": "Significant fluctuations in fraud patterns increase uncertainty"
            })
        else:
            factors.append({
                "factor": "Low Volatility",
                "weight": 0.2,
                "explanation": "Consistent fraud patterns provide stable predictions"
            })
        
        # Recent activity factor
        if features.get("recent_spike", False):
            factors.append({
                "factor": "Recent Spike",
                "weight": 0.3,
                "explanation": "Recent increase in fraud activity detected"
            })
        else:
            factors.append({
                "factor": "Baseline Activity",
                "weight": 0.2,
                "explanation": "Current activity levels within normal range"
            })
        
        return factors[:3]  # Return top 3 factors
    
    def get_stored_forecasts(self, dimension: str, period: str) -> List[Dict[str, Any]]:
        """Retrieve stored forecasts from database"""
        forecasts = self.db.query(Forecast).filter(
            Forecast.dimension == dimension,
            Forecast.period == period
        ).order_by(desc(Forecast.created_at)).all()
        
        result = []
        for forecast in forecasts:
            result.append({
                "key": forecast.key,
                "risk_score": forecast.risk_score,
                "confidence_interval": [forecast.confidence_min, forecast.confidence_max],
                "rationale": forecast.rationale,
                "contributing_factors": forecast.contributing_factors,
                "features": forecast.features,
                "created_at": forecast.created_at.isoformat()
            })
        
        return result
    
    def get_forecast_accuracy_metrics(self, dimension: str) -> Dict[str, Any]:
        """Calculate historical forecast accuracy metrics"""
        # This would compare past forecasts with actual outcomes
        # For now, return mock metrics
        return {
            "overall_accuracy": 78.5,
            "high_risk_precision": 82.3,
            "medium_risk_precision": 75.1,
            "low_risk_precision": 80.7,
            "trend_accuracy": 71.2,
            "confidence_calibration": 76.8
        }