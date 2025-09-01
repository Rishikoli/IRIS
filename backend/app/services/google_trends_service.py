"""
Google Trends API Integration Service
Monitors fraud-related keyword trends by region for early fraud detection
"""

import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
import random
import os
from app.services.gemini_service import GeminiService

# Try to import pytrends for real Google Trends data
try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    PYTRENDS_AVAILABLE = False
    print("pytrends not available, using mock data for Google Trends")

class TrendData(BaseModel):
    keyword: str
    region: str
    search_volume: int  # Relative search volume (0-100)
    trend_direction: str  # 'rising', 'falling', 'stable'
    timeframe: str  # '1h', '1d', '7d', '30d'
    timestamp: datetime

class RegionalSpike(BaseModel):
    region: str
    keyword: str
    spike_intensity: float  # Multiplier of normal volume
    duration_hours: int
    fraud_correlation: float  # 0-100

class TrendCorrelation(BaseModel):
    keyword: str
    region: str
    correlation_strength: float  # 0-100
    fraud_cases_count: int
    analysis_summary: str

class GoogleTrendsService:
    def __init__(self):
        self.gemini_service = GeminiService()
        self.use_real_api = PYTRENDS_AVAILABLE and os.getenv("USE_REAL_TRENDS", "false").lower() == "true"
        
        if self.use_real_api:
            self.pytrends = TrendReq(hl='en-US', tz=360)  # Indian timezone
        
        # Fraud-related keywords to monitor
        self.fraud_keywords = [
            "stock tip scam", "investment fraud", "fake sebi", "pump dump",
            "guaranteed returns", "quick money scheme", "trading scam",
            "fake advisor", "ponzi scheme", "market manipulation",
            "investment chit fund", "binary options scam", "crypto fraud"
        ]
        
        # Indian regions to monitor (Google Trends geo codes for Indian states/cities)
        self.indian_regions = {
            "Mumbai": "IN-MH",  # Maharashtra
            "Delhi": "IN-DL",   # Delhi
            "Bangalore": "IN-KA",  # Karnataka
            "Chennai": "IN-TN",    # Tamil Nadu
            "Kolkata": "IN-WB",    # West Bengal
            "Hyderabad": "IN-TG",  # Telangana
            "Pune": "IN-MH",       # Maharashtra
            "Ahmedabad": "IN-GJ",  # Gujarat
            "Jaipur": "IN-RJ",     # Rajasthan
            "Lucknow": "IN-UP"     # Uttar Pradesh
        }
    
    async def fetch_fraud_trends(self, regions: Optional[List[str]] = None, timeframe: str = "7d") -> List[TrendData]:
        """Fetch Google Trends data for fraud-related keywords by region"""
        if not regions:
            regions = list(self.indian_regions.keys())
        
        try:
            if self.use_real_api:
                return await self._fetch_real_trends(regions, timeframe)
            else:
                return await self._fetch_mock_trends(regions, timeframe)
            
        except Exception as e:
            print(f"Error fetching Google Trends data: {e}")
            return await self._fetch_mock_trends(regions, timeframe)
    
    async def _fetch_real_trends(self, regions: List[str], timeframe: str) -> List[TrendData]:
        """Fetch real Google Trends data using pytrends"""
        trends_data = []
        
        try:
            # Convert timeframe to pytrends format
            timeframe_map = {
                "1h": "now 1-H",
                "1d": "now 1-d", 
                "7d": "now 7-d",
                "30d": "today 1-m"
            }
            pytrends_timeframe = timeframe_map.get(timeframe, "now 7-d")
            
            # Process keywords in batches (pytrends limit is 5 keywords per request)
            keyword_batches = [self.fraud_keywords[i:i+5] for i in range(0, len(self.fraud_keywords), 5)]
            
            for region in regions:
                geo_code = self.indian_regions.get(region, "IN")  # Default to India
                
                for keyword_batch in keyword_batches:
                    try:
                        # Build payload for pytrends
                        self.pytrends.build_payload(
                            keyword_batch, 
                            cat=0, 
                            timeframe=pytrends_timeframe, 
                            geo=geo_code, 
                            gprop=''
                        )
                        
                        # Get interest over time
                        interest_df = self.pytrends.interest_over_time()
                        
                        if not interest_df.empty:
                            # Process each keyword
                            for keyword in keyword_batch:
                                if keyword in interest_df.columns:
                                    # Get latest values
                                    latest_values = interest_df[keyword].tail(7)  # Last 7 data points
                                    current_volume = int(latest_values.iloc[-1]) if len(latest_values) > 0 else 0
                                    
                                    # Calculate trend direction
                                    if len(latest_values) >= 2:
                                        trend_slope = latest_values.iloc[-1] - latest_values.iloc[0]
                                        if trend_slope > 5:
                                            trend_direction = "rising"
                                        elif trend_slope < -5:
                                            trend_direction = "falling"
                                        else:
                                            trend_direction = "stable"
                                    else:
                                        trend_direction = "stable"
                                    
                                    trend_data = TrendData(
                                        keyword=keyword,
                                        region=region,
                                        search_volume=current_volume,
                                        trend_direction=trend_direction,
                                        timeframe=timeframe,
                                        timestamp=datetime.now()
                                    )
                                    trends_data.append(trend_data)
                        
                        # Add delay to respect rate limits
                        await asyncio.sleep(1)
                        
                    except Exception as e:
                        print(f"Error fetching trends for {keyword_batch} in {region}: {e}")
                        continue
            
            return trends_data
            
        except Exception as e:
            print(f"Error in real trends fetching: {e}")
            return []
    
    async def _fetch_mock_trends(self, regions: List[str], timeframe: str) -> List[TrendData]:
        """Generate mock trends data for demo/fallback"""
        trends_data = []
        
        for region in regions:
            for keyword in self.fraud_keywords[:5]:  # Limit for demo
                # Generate realistic mock data
                base_volume = random.randint(10, 80)
                
                # Add some regional variation
                if region in ["Mumbai", "Delhi", "Bangalore"]:
                    base_volume += random.randint(10, 20)  # Higher activity in major cities
                
                # Simulate trend direction
                trend_directions = ["rising", "falling", "stable"]
                weights = [0.3, 0.2, 0.5]  # More stable trends
                trend_direction = random.choices(trend_directions, weights=weights)[0]
                
                trend_data = TrendData(
                    keyword=keyword,
                    region=region,
                    search_volume=base_volume,
                    trend_direction=trend_direction,
                    timeframe=timeframe,
                    timestamp=datetime.now()
                )
                trends_data.append(trend_data)
        
        return trends_data
    
    async def analyze_search_spikes(self, trend_data: List[TrendData]) -> List[RegionalSpike]:
        """Identify regions with unusual spikes in fraud-related searches"""
        spikes = []
        
        # Group data by region
        region_data = {}
        for trend in trend_data:
            if trend.region not in region_data:
                region_data[trend.region] = []
            region_data[trend.region].append(trend)
        
        for region, trends in region_data.items():
            # Calculate average search volume for the region
            avg_volume = sum(t.search_volume for t in trends) / len(trends)
            
            # Identify spikes (volume significantly above average)
            for trend in trends:
                if trend.search_volume > avg_volume * 1.5:  # 50% above average
                    spike_intensity = trend.search_volume / avg_volume
                    
                    spike = RegionalSpike(
                        region=region,
                        keyword=trend.keyword,
                        spike_intensity=spike_intensity,
                        duration_hours=random.randint(2, 24),  # Mock duration
                        fraud_correlation=min(100, spike_intensity * 30)  # Higher spikes = higher correlation
                    )
                    spikes.append(spike)
        
        return spikes
    
    async def correlate_trends_with_fraud(self, trends: List[TrendData], fraud_cases: List[Dict]) -> List[TrendCorrelation]:
        """Correlate search trends with actual fraud case patterns"""
        correlations = []
        
        try:
            # Group fraud cases by region (mock implementation)
            region_fraud_counts = {}
            for case in fraud_cases:
                region = case.get('region', 'Unknown')
                region_fraud_counts[region] = region_fraud_counts.get(region, 0) + 1
            
            # Analyze correlation for each trend
            for trend in trends:
                fraud_count = region_fraud_counts.get(trend.region, 0)
                
                # Calculate correlation strength based on search volume and fraud cases
                if fraud_count > 0:
                    correlation_strength = min(100, (trend.search_volume * fraud_count) / 10)
                else:
                    correlation_strength = trend.search_volume * 0.3  # Lower correlation without cases
                
                # Generate analysis summary using AI
                analysis_summary = await self._generate_correlation_analysis(trend, fraud_count)
                
                correlation = TrendCorrelation(
                    keyword=trend.keyword,
                    region=trend.region,
                    correlation_strength=correlation_strength,
                    fraud_cases_count=fraud_count,
                    analysis_summary=analysis_summary
                )
                correlations.append(correlation)
            
            return correlations
            
        except Exception as e:
            print(f"Error correlating trends with fraud: {e}")
            return []
    
    async def _generate_correlation_analysis(self, trend: TrendData, fraud_count: int) -> str:
        """Generate AI-powered analysis of trend-fraud correlation"""
        try:
            prompt = f"""
            Analyze the correlation between search trends and fraud activity:
            
            Keyword: "{trend.keyword}"
            Region: {trend.region}
            Search Volume: {trend.search_volume}/100
            Trend Direction: {trend.trend_direction}
            Actual Fraud Cases: {fraud_count}
            
            Provide a brief analysis (2-3 sentences) explaining:
            1. What this correlation suggests about fraud activity
            2. Whether the search volume aligns with actual cases
            3. Any actionable insights for fraud prevention
            
            Keep it concise and professional.
            """
            
            analysis = await self.gemini_service.analyze_text(prompt)
            return analysis.strip()
            
        except Exception as e:
            print(f"Error generating correlation analysis: {e}")
            return f"Search volume of {trend.search_volume} for '{trend.keyword}' in {trend.region} with {fraud_count} reported cases suggests moderate correlation."
    
    async def get_trending_fraud_keywords(self, region: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get currently trending fraud-related keywords for a specific region"""
        try:
            # Mock implementation - in production, this would use real Google Trends API
            trending_keywords = []
            
            for keyword in self.fraud_keywords[:limit]:
                volume = random.randint(20, 90)
                change = random.randint(-30, 50)  # Percentage change
                
                trending_keywords.append({
                    "keyword": keyword,
                    "volume": volume,
                    "change_percent": change,
                    "trend": "rising" if change > 10 else "falling" if change < -10 else "stable",
                    "region": region
                })
            
            # Sort by volume descending
            trending_keywords.sort(key=lambda x: x["volume"], reverse=True)
            
            return trending_keywords
            
        except Exception as e:
            print(f"Error getting trending keywords: {e}")
            return []
    
    async def detect_emerging_fraud_patterns(self, trends: List[TrendData]) -> List[Dict[str, Any]]:
        """Detect emerging fraud patterns from search trend analysis"""
        try:
            patterns = []
            
            # Group trends by keyword to identify patterns
            keyword_trends = {}
            for trend in trends:
                if trend.keyword not in keyword_trends:
                    keyword_trends[trend.keyword] = []
                keyword_trends[trend.keyword].append(trend)
            
            for keyword, keyword_data in keyword_trends.items():
                # Calculate average volume and identify rising trends
                avg_volume = sum(t.search_volume for t in keyword_data) / len(keyword_data)
                rising_regions = [t.region for t in keyword_data if t.trend_direction == "rising"]
                
                if len(rising_regions) >= 3 and avg_volume > 40:  # Pattern threshold
                    pattern = {
                        "pattern_type": "emerging_fraud_scheme",
                        "keyword": keyword,
                        "affected_regions": rising_regions,
                        "average_volume": avg_volume,
                        "severity": "high" if avg_volume > 70 else "medium",
                        "description": f"Rising search activity for '{keyword}' detected across {len(rising_regions)} regions",
                        "recommended_action": "Increase monitoring and issue public awareness alerts"
                    }
                    patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            print(f"Error detecting fraud patterns: {e}")
            return []