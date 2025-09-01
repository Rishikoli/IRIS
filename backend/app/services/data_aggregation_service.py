"""
Data Aggregation Service
Combines multi-source data (FMP, Google Trends, Economic Times) for unified fraud analysis
"""

import asyncio
from typing import List, Dict, Optional, Any, Union
from datetime import datetime, timedelta
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.services.fmp_service import FMPIntegrationService, StockData, MarketNews
from app.services.google_trends_service import GoogleTrendsService, TrendData
from app.services.economic_times_service import EconomicTimesScrapingService, NewsArticle
from app.services.gemini_service import GeminiService
from app.models import DataIndicator, CrossSourceCorrelation, FMPMarketData, GoogleTrendsData, EconomicTimesArticle
import uuid

class ConsolidatedIndicator(BaseModel):
    sector: Optional[str] = None
    region: Optional[str] = None
    indicator_type: str
    source: str
    relevance_score: float
    summary: str
    details: Dict[str, Any]
    timestamp: datetime

class CrossSourceCorrelationResult(BaseModel):
    correlation_type: str
    source_1: str
    source_1_data: Dict[str, Any]
    source_2: str
    source_2_data: Dict[str, Any]
    correlation_strength: float
    fraud_implication: str
    analysis_summary: str

class MultiSourceDataSummary(BaseModel):
    total_indicators: int
    high_relevance_count: int
    sources_active: List[str]
    top_correlations: List[CrossSourceCorrelationResult]
    fraud_risk_level: str  # low, medium, high
    key_insights: List[str]

class DataAggregationService:
    def __init__(self):
        self.fmp_service = FMPIntegrationService()
        self.trends_service = GoogleTrendsService()
        self.et_service = EconomicTimesScrapingService()
        self.gemini_service = GeminiService()
        
        # Sector-region mapping for Indian markets
        self.sector_region_mapping = {
            "Technology": ["Bangalore", "Hyderabad", "Chennai", "Pune"],
            "Banking": ["Mumbai", "Delhi", "Bangalore", "Chennai"],
            "Pharma": ["Hyderabad", "Mumbai", "Ahmedabad"],
            "Energy": ["Mumbai", "Delhi", "Chennai"],
            "FMCG": ["Mumbai", "Delhi", "Kolkata"],
            "Auto": ["Chennai", "Delhi", "Pune"],
            "Telecom": ["Mumbai", "Delhi", "Bangalore"],
            "Real Estate": ["Mumbai", "Delhi", "Bangalore", "Pune"]
        }
    
    async def generate_consolidated_indicators(self, heatmap_data: List[Dict]) -> List[ConsolidatedIndicator]:
        """Generate multi-source overlay indicators for heatmap visualization"""
        try:
            indicators = []
            
            # Fetch data from all sources
            fmp_data = await self.fmp_service.fetch_market_data()
            fmp_news = await self.fmp_service.fetch_financial_news()
            trends_data = await self.trends_service.fetch_fraud_trends()
            et_articles = await self.et_service.scrape_latest_news()
            
            # Process FMP market data indicators
            for stock in fmp_data:
                if stock.unusual_activity:
                    # Map stock to sectors and regions
                    sectors = self._map_stock_to_sectors(stock.symbol)
                    for sector in sectors:
                        regions = self.sector_region_mapping.get(sector, ["Mumbai"])
                        for region in regions:
                            relevance_score = await self.fmp_service.score_fraud_relevance(stock.dict())
                            
                            indicator = ConsolidatedIndicator(
                                sector=sector,
                                region=region,
                                indicator_type="market_anomaly",
                                source="fmp",
                                relevance_score=relevance_score,
                                summary=f"Unusual activity in {stock.symbol}: {stock.change_percent:+.2f}%",
                                details={
                                    "symbol": stock.symbol,
                                    "price": stock.price,
                                    "change_percent": stock.change_percent,
                                    "volume": stock.volume,
                                    "unusual_activity": stock.unusual_activity
                                },
                                timestamp=datetime.now()
                            )
                            indicators.append(indicator)
            
            # Process FMP news indicators
            for news in fmp_news:
                relevance_score = await self.fmp_service.score_fraud_relevance(news.dict())
                if relevance_score > 40:  # Only include relevant news
                    # Map news to sectors based on mentioned symbols
                    for symbol in news.symbols:
                        sectors = self._map_stock_to_sectors(symbol)
                        for sector in sectors:
                            regions = self.sector_region_mapping.get(sector, ["Mumbai"])
                            for region in regions:
                                indicator = ConsolidatedIndicator(
                                    sector=sector,
                                    region=region,
                                    indicator_type="financial_news",
                                    source="fmp",
                                    relevance_score=relevance_score,
                                    summary=news.title[:100] + "...",
                                    details={
                                        "title": news.title,
                                        "content": news.content[:500],
                                        "url": news.url,
                                        "symbols": news.symbols,
                                        "sentiment": news.sentiment
                                    },
                                    timestamp=news.published_at
                                )
                                indicators.append(indicator)
            
            # Process Google Trends indicators
            trend_spikes = await self.trends_service.analyze_search_spikes(trends_data)
            for spike in trend_spikes:
                if spike.fraud_correlation > 50:  # Only include significant correlations
                    # Map to sectors based on keyword
                    sectors = self._map_keyword_to_sectors(spike.keyword)
                    for sector in sectors:
                        indicator = ConsolidatedIndicator(
                            sector=sector,
                            region=spike.region,
                            indicator_type="search_spike",
                            source="google_trends",
                            relevance_score=spike.fraud_correlation,
                            summary=f"Search spike for '{spike.keyword}' in {spike.region}",
                            details={
                                "keyword": spike.keyword,
                                "region": spike.region,
                                "spike_intensity": spike.spike_intensity,
                                "duration_hours": spike.duration_hours,
                                "fraud_correlation": spike.fraud_correlation
                            },
                            timestamp=datetime.now()
                        )
                        indicators.append(indicator)
            
            # Process Economic Times indicators
            for article in et_articles:
                if article.fraud_relevance_score > 40:
                    # Map articles to sectors based on content
                    sectors = self._map_article_to_sectors(article)
                    regions = self._map_article_to_regions(article)
                    
                    for sector in sectors:
                        for region in regions:
                            indicator = ConsolidatedIndicator(
                                sector=sector,
                                region=region,
                                indicator_type="news_alert",
                                source="economic_times",
                                relevance_score=article.fraud_relevance_score,
                                summary=article.title[:100] + "...",
                                details={
                                    "title": article.title,
                                    "content": article.content[:500],
                                    "url": article.url,
                                    "category": article.category,
                                    "regulatory_mentions": article.regulatory_mentions,
                                    "sentiment": article.sentiment
                                },
                                timestamp=article.published_at
                            )
                            indicators.append(indicator)
            
            return indicators
            
        except Exception as e:
            print(f"Error generating consolidated indicators: {e}")
            return []
    
    async def correlate_multi_source_data(self, fmp_data: List[Dict], trends_data: List[Dict], news_data: List[Dict]) -> List[CrossSourceCorrelationResult]:
        """Correlate data across FMP, Google Trends, and Economic Times"""
        try:
            correlations = []
            
            # Correlate FMP market anomalies with Google Trends spikes
            for fmp_item in fmp_data:
                if fmp_item.get("unusual_activity"):
                    symbol = fmp_item.get("symbol", "")
                    
                    # Look for related trend spikes
                    for trend_item in trends_data:
                        keyword = trend_item.get("keyword", "")
                        if (symbol.replace(".NS", "").lower() in keyword.lower() or
                            any(term in keyword.lower() for term in ["stock", "trading", "investment"])):
                            
                            correlation_strength = min(100, 
                                (fmp_item.get("change_percent", 0) * 2) + 
                                (trend_item.get("search_volume", 0) * 0.8)
                            )
                            
                            if correlation_strength > 30:
                                analysis = await self._generate_correlation_analysis(fmp_item, trend_item, "market_trend")
                                
                                correlation = CrossSourceCorrelationResult(
                                    correlation_type="market_trend_spike",
                                    source_1="fmp",
                                    source_1_data=fmp_item,
                                    source_2="google_trends",
                                    source_2_data=trend_item,
                                    correlation_strength=correlation_strength,
                                    fraud_implication="Potential pump-and-dump scheme",
                                    analysis_summary=analysis
                                )
                                correlations.append(correlation)
            
            # Correlate Economic Times news with Google Trends
            for news_item in news_data:
                if news_item.get("fraud_relevance_score", 0) > 60:
                    # Look for related trend activity
                    for trend_item in trends_data:
                        keyword_match = any(
                            keyword in news_item.get("title", "").lower() 
                            for keyword in trend_item.get("keyword", "").split()
                        )
                        
                        if keyword_match:
                            correlation_strength = min(100,
                                news_item.get("fraud_relevance_score", 0) * 0.7 +
                                trend_item.get("search_volume", 0) * 0.5
                            )
                            
                            if correlation_strength > 40:
                                analysis = await self._generate_correlation_analysis(news_item, trend_item, "news_trend")
                                
                                correlation = CrossSourceCorrelationResult(
                                    correlation_type="news_search_correlation",
                                    source_1="economic_times",
                                    source_1_data=news_item,
                                    source_2="google_trends",
                                    source_2_data=trend_item,
                                    correlation_strength=correlation_strength,
                                    fraud_implication="Public awareness of fraud scheme",
                                    analysis_summary=analysis
                                )
                                correlations.append(correlation)
            
            # Sort by correlation strength
            correlations.sort(key=lambda x: x.correlation_strength, reverse=True)
            
            return correlations[:10]  # Return top 10 correlations
            
        except Exception as e:
            print(f"Error correlating multi-source data: {e}")
            return []
    
    async def store_indicators_in_db(self, db: Session, indicators: List[ConsolidatedIndicator]) -> List[str]:
        """Store consolidated indicators in database"""
        try:
            stored_ids = []
            
            for indicator in indicators:
                # Create database record
                db_indicator = DataIndicator(
                    id=str(uuid.uuid4()),
                    heatmap_sector=indicator.sector,
                    heatmap_region=indicator.region,
                    indicator_type=indicator.indicator_type,
                    source=indicator.source,
                    relevance_score=int(indicator.relevance_score),
                    summary=indicator.summary,
                    details=indicator.details,
                    active=True,
                    expires_at=datetime.now() + timedelta(hours=24),  # Indicators expire after 24 hours
                    created_at=indicator.timestamp
                )
                
                db.add(db_indicator)
                stored_ids.append(db_indicator.id)
            
            db.commit()
            return stored_ids
            
        except Exception as e:
            print(f"Error storing indicators in database: {e}")
            db.rollback()
            return []
    
    async def get_multi_source_summary(self, indicators: List[ConsolidatedIndicator], correlations: List[CrossSourceCorrelationResult]) -> MultiSourceDataSummary:
        """Generate summary of multi-source data analysis"""
        try:
            high_relevance_count = len([i for i in indicators if i.relevance_score > 70])
            sources_active = list(set([i.source for i in indicators]))
            
            # Determine overall fraud risk level
            if high_relevance_count > 5 or any(c.correlation_strength > 80 for c in correlations):
                fraud_risk_level = "high"
            elif high_relevance_count > 2 or any(c.correlation_strength > 60 for c in correlations):
                fraud_risk_level = "medium"
            else:
                fraud_risk_level = "low"
            
            # Generate key insights
            key_insights = []
            
            if high_relevance_count > 0:
                key_insights.append(f"{high_relevance_count} high-relevance fraud indicators detected")
            
            if len(correlations) > 0:
                key_insights.append(f"{len(correlations)} cross-source correlations identified")
            
            # Add source-specific insights
            fmp_indicators = [i for i in indicators if i.source == "fmp"]
            if fmp_indicators:
                key_insights.append(f"Market anomalies detected in {len(set([i.sector for i in fmp_indicators]))} sectors")
            
            trends_indicators = [i for i in indicators if i.source == "google_trends"]
            if trends_indicators:
                key_insights.append(f"Search spikes detected in {len(set([i.region for i in trends_indicators]))} regions")
            
            return MultiSourceDataSummary(
                total_indicators=len(indicators),
                high_relevance_count=high_relevance_count,
                sources_active=sources_active,
                top_correlations=correlations[:5],  # Top 5 correlations
                fraud_risk_level=fraud_risk_level,
                key_insights=key_insights
            )
            
        except Exception as e:
            print(f"Error generating multi-source summary: {e}")
            return MultiSourceDataSummary(
                total_indicators=0,
                high_relevance_count=0,
                sources_active=[],
                top_correlations=[],
                fraud_risk_level="low",
                key_insights=[]
            )
    
    def _map_stock_to_sectors(self, symbol: str) -> List[str]:
        """Map stock symbol to relevant sectors"""
        symbol_clean = symbol.replace(".NS", "").upper()
        
        # Simple mapping based on known symbols
        sector_mapping = {
            "TCS": ["Technology"], "INFY": ["Technology"], "HCLTECH": ["Technology"],
            "HDFCBANK": ["Banking"], "ICICIBANK": ["Banking"], "SBIN": ["Banking"],
            "RELIANCE": ["Energy", "Telecom"], "BHARTIARTL": ["Telecom"],
            "MARUTI": ["Auto"], "HINDUNILVR": ["FMCG"], "ITC": ["FMCG"]
        }
        
        return sector_mapping.get(symbol_clean, ["Technology"])  # Default to Technology
    
    def _map_keyword_to_sectors(self, keyword: str) -> List[str]:
        """Map search keyword to relevant sectors"""
        keyword_lower = keyword.lower()
        
        if any(term in keyword_lower for term in ["stock", "trading", "investment"]):
            return ["Banking", "Technology"]
        elif any(term in keyword_lower for term in ["loan", "credit", "banking"]):
            return ["Banking"]
        elif any(term in keyword_lower for term in ["crypto", "bitcoin", "digital"]):
            return ["Technology", "Banking"]
        else:
            return ["Banking"]  # Default sector for fraud keywords
    
    def _map_article_to_sectors(self, article: NewsArticle) -> List[str]:
        """Map news article to relevant sectors"""
        content_lower = (article.title + " " + article.content).lower()
        sectors = []
        
        if any(term in content_lower for term in ["technology", "tech", "ai", "digital"]):
            sectors.append("Technology")
        if any(term in content_lower for term in ["banking", "bank", "finance", "loan"]):
            sectors.append("Banking")
        if any(term in content_lower for term in ["pharma", "drug", "medicine"]):
            sectors.append("Pharma")
        if any(term in content_lower for term in ["energy", "oil", "gas", "power"]):
            sectors.append("Energy")
        
        return sectors if sectors else ["Banking"]  # Default to Banking
    
    def _map_article_to_regions(self, article: NewsArticle) -> List[str]:
        """Map news article to relevant regions"""
        content_lower = (article.title + " " + article.content).lower()
        regions = []
        
        for region in self.sector_region_mapping.values():
            for city in region:
                if city.lower() in content_lower:
                    regions.append(city)
        
        return regions if regions else ["Mumbai", "Delhi"]  # Default to major cities
    
    async def _generate_correlation_analysis(self, data1: Dict, data2: Dict, correlation_type: str) -> str:
        """Generate AI-powered correlation analysis"""
        try:
            prompt = f"""
            Analyze the correlation between these two data points:
            
            Data Source 1: {data1}
            Data Source 2: {data2}
            Correlation Type: {correlation_type}
            
            Provide a brief analysis (2-3 sentences) explaining:
            1. What this correlation suggests about potential fraud activity
            2. The significance of this pattern
            3. Recommended monitoring actions
            
            Keep it concise and actionable.
            """
            
            analysis = await self.gemini_service.analyze_text(prompt)
            return analysis.strip()
            
        except Exception as e:
            print(f"Error generating correlation analysis: {e}")
            return f"Correlation detected between {correlation_type} data sources requiring further investigation."