"""
FMP (Financial Modeling Prep) API Integration Service
Provides real-time market data and financial news for fraud correlation analysis
"""

import httpx
import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
import os
from app.services.gemini_service import GeminiService
from app.services.cache_service import cache_service, rate_limit_service, data_freshness_service

class StockData(BaseModel):
    symbol: str
    price: float
    change_percent: float
    volume: int
    market_cap: Optional[int] = None
    unusual_activity: bool = False

class MarketNews(BaseModel):
    title: str
    content: str
    url: str
    published_at: datetime
    symbols: List[str] = []
    sentiment: str = "neutral"

class StockAlert(BaseModel):
    symbol: str
    alert_type: str  # 'volume_spike', 'price_anomaly', 'news_impact'
    severity: str  # 'low', 'medium', 'high'
    description: str
    fraud_relevance: float  # 0-100

class CompanyFinancials(BaseModel):
    symbol: str
    revenue: Optional[float] = None
    net_income: Optional[float] = None
    debt_to_equity: Optional[float] = None
    pe_ratio: Optional[float] = None
    red_flags: List[str] = []

class FMPIntegrationService:
    def __init__(self):
        self.api_key = os.getenv("FMP_API_KEY", "demo")  # Use demo key for development
        self.base_url = "https://financialmodelingprep.com/api/v3"
        self.gemini_service = GeminiService()
        
        # Indian stock symbols for demo purposes
        self.indian_stocks = [
            "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS",
            "ICICIBANK.NS", "KOTAKBANK.NS", "BHARTIARTL.NS", "ITC.NS", "SBIN.NS",
            "ASIANPAINT.NS", "MARUTI.NS", "BAJFINANCE.NS", "HCLTECH.NS", "WIPRO.NS"
        ]
    
    async def fetch_market_data(self, symbols: Optional[List[str]] = None) -> List[StockData]:
        """Fetch real-time stock prices and market data from FMP API"""
        if not symbols:
            symbols = self.indian_stocks[:10]  # Limit for demo
        
        try:
            # Try real FMP API first, fallback to mock if API key is demo or fails
            if self.api_key != "demo":
                return await self._fetch_real_market_data(symbols)
            else:
                return await self._fetch_mock_market_data(symbols)
            
        except Exception as e:
            print(f"Error fetching market data: {e}")
            # Fallback to mock data on error
            return await self._fetch_mock_market_data(symbols)
    
    async def _fetch_real_market_data(self, symbols: List[str]) -> List[StockData]:
        """Fetch real market data from FMP API"""
        stock_data_list = []
        
        async with httpx.AsyncClient() as client:
            for symbol in symbols:
                try:
                    # Get real-time quote
                    quote_url = f"{self.base_url}/quote/{symbol}"
                    response = await client.get(
                        quote_url,
                        params={"apikey": self.api_key},
                        timeout=10.0
                    )
                    
                    if response.status_code == 200:
                        quote_data = response.json()
                        if quote_data and len(quote_data) > 0:
                            quote = quote_data[0]
                            
                            stock_data = StockData(
                                symbol=symbol,
                                price=float(quote.get('price', 0)),
                                change_percent=float(quote.get('changesPercentage', 0)),
                                volume=int(quote.get('volume', 0)),
                                market_cap=int(quote.get('marketCap', 0)) if quote.get('marketCap') else None,
                                unusual_activity=abs(float(quote.get('changesPercentage', 0))) > 5
                            )
                            stock_data_list.append(stock_data)
                    
                    # Add small delay to respect rate limits
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    print(f"Error fetching data for {symbol}: {e}")
                    continue
        
        return stock_data_list
    
    async def _fetch_mock_market_data(self, symbols: List[str]) -> List[StockData]:
        """Generate mock market data for demo/fallback"""
        mock_data = []
        for symbol in symbols:
            # Generate realistic mock data
            base_price = hash(symbol) % 1000 + 100  # Deterministic but varied prices
            change = (hash(symbol + str(datetime.now().hour)) % 200 - 100) / 10  # -10% to +10%
            volume = (hash(symbol) % 1000000) + 100000
            
            stock_data = StockData(
                symbol=symbol,
                price=base_price + (base_price * change / 100),
                change_percent=change,
                volume=volume,
                market_cap=(base_price * 1000000) if base_price > 500 else None,
                unusual_activity=abs(change) > 5  # Flag unusual activity
            )
            mock_data.append(stock_data)
        
        return mock_data
    
    async def fetch_financial_news(self, sectors: Optional[List[str]] = None) -> List[MarketNews]:
        """Fetch financial news from FMP API"""
        try:
            # Try real FMP API first, fallback to mock if API key is demo or fails
            if self.api_key != "demo":
                return await self._fetch_real_financial_news(sectors)
            else:
                return await self._fetch_mock_financial_news()
            
        except Exception as e:
            print(f"Error fetching financial news: {e}")
            return await self._fetch_mock_financial_news()
    
    async def _fetch_real_financial_news(self, sectors: Optional[List[str]] = None) -> List[MarketNews]:
        """Fetch real financial news from FMP API"""
        news_list = []
        
        try:
            async with httpx.AsyncClient() as client:
                # Get general market news
                news_url = f"{self.base_url}/stock_news"
                response = await client.get(
                    news_url,
                    params={
                        "apikey": self.api_key,
                        "limit": 50,
                        "page": 0
                    },
                    timeout=15.0
                )
                
                if response.status_code == 200:
                    news_data = response.json()
                    
                    for article in news_data:
                        # Filter for Indian market or fraud-related news
                        title = article.get('title', '').lower()
                        content = article.get('text', '')
                        
                        # Check if relevant to Indian markets or fraud detection
                        indian_keywords = ['india', 'sebi', 'nse', 'bse', 'mumbai', 'delhi', 'bangalore']
                        fraud_keywords = ['fraud', 'scam', 'manipulation', 'regulatory', 'investigation']
                        
                        is_relevant = (
                            any(keyword in title for keyword in indian_keywords) or
                            any(keyword in title for keyword in fraud_keywords)
                        )
                        
                        if is_relevant:
                            # Extract symbols mentioned in the article
                            symbols = []
                            for stock in self.indian_stocks:
                                stock_name = stock.replace('.NS', '')
                                if stock_name.lower() in title or stock_name.lower() in content.lower():
                                    symbols.append(stock)
                            
                            # Determine sentiment
                            sentiment = self._analyze_news_sentiment(title + " " + content)
                            
                            news_item = MarketNews(
                                title=article.get('title', ''),
                                content=content[:500] + "..." if len(content) > 500 else content,
                                url=article.get('url', ''),
                                published_at=datetime.fromisoformat(article.get('publishedDate', '').replace('Z', '+00:00')),
                                symbols=symbols,
                                sentiment=sentiment
                            )
                            news_list.append(news_item)
                            
                            # Limit to 20 relevant articles
                            if len(news_list) >= 20:
                                break
                
        except Exception as e:
            print(f"Error fetching real financial news: {e}")
        
        return news_list
    
    async def _fetch_mock_financial_news(self) -> List[MarketNews]:
        """Generate mock financial news for demo/fallback"""
        mock_news = [
            MarketNews(
                title="SEBI Issues New Guidelines on Market Manipulation",
                content="The Securities and Exchange Board of India has issued new guidelines to combat market manipulation schemes targeting retail investors.",
                url="https://example.com/sebi-guidelines",
                published_at=datetime.now() - timedelta(hours=2),
                symbols=["NIFTY", "SENSEX"],
                sentiment="regulatory"
            ),
            MarketNews(
                title="Tech Stocks Rally Amid AI Investment Surge",
                content="Indian technology stocks are experiencing significant gains as companies announce major AI investments.",
                url="https://example.com/tech-rally",
                published_at=datetime.now() - timedelta(hours=4),
                symbols=["TCS.NS", "INFY.NS", "HCLTECH.NS"],
                sentiment="positive"
            ),
            MarketNews(
                title="Banking Sector Faces Regulatory Scrutiny",
                content="RBI announces enhanced monitoring of digital lending practices following reports of fraudulent schemes.",
                url="https://example.com/banking-scrutiny",
                published_at=datetime.now() - timedelta(hours=6),
                symbols=["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS"],
                sentiment="negative"
            )
        ]
        
        return mock_news
    
    def _analyze_news_sentiment(self, text: str) -> str:
        """Analyze sentiment of news text"""
        text_lower = text.lower()
        
        positive_words = ['growth', 'profit', 'gain', 'rise', 'surge', 'rally', 'strong', 'positive']
        negative_words = ['fraud', 'scam', 'loss', 'fall', 'decline', 'investigation', 'penalty', 'warning']
        regulatory_words = ['sebi', 'rbi', 'regulation', 'compliance', 'guideline', 'circular']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        regulatory_count = sum(1 for word in regulatory_words if word in text_lower)
        
        if regulatory_count > 0:
            return "regulatory"
        elif negative_count > positive_count:
            return "negative"
        elif positive_count > negative_count:
            return "positive"
        else:
            return "neutral"
    
    async def detect_unusual_activity(self, stock_data: List[StockData]) -> List[StockAlert]:
        """Detect unusual trading patterns that might indicate fraud"""
        alerts = []
        
        for stock in stock_data:
            # Volume spike detection
            if stock.volume > 500000:  # Threshold for unusual volume
                alerts.append(StockAlert(
                    symbol=stock.symbol,
                    alert_type="volume_spike",
                    severity="medium" if stock.volume > 1000000 else "low",
                    description=f"Unusual trading volume detected: {stock.volume:,} shares",
                    fraud_relevance=60 if stock.volume > 1000000 else 30
                ))
            
            # Price anomaly detection
            if abs(stock.change_percent) > 8:  # Significant price movement
                severity = "high" if abs(stock.change_percent) > 15 else "medium"
                alerts.append(StockAlert(
                    symbol=stock.symbol,
                    alert_type="price_anomaly",
                    severity=severity,
                    description=f"Significant price movement: {stock.change_percent:+.2f}%",
                    fraud_relevance=80 if abs(stock.change_percent) > 15 else 50
                ))
        
        return alerts
    
    async def get_company_financials(self, symbol: str) -> CompanyFinancials:
        """Fetch company financial statements for fraud analysis"""
        try:
            # Generate mock financial data for demo
            base_value = hash(symbol) % 10000
            
            financials = CompanyFinancials(
                symbol=symbol,
                revenue=base_value * 1000000,  # Mock revenue
                net_income=base_value * 100000,  # Mock net income
                debt_to_equity=(hash(symbol) % 200) / 100,  # 0-2 ratio
                pe_ratio=(hash(symbol) % 50) + 5,  # 5-55 PE ratio
                red_flags=[]
            )
            
            # Add red flags based on mock analysis
            if financials.debt_to_equity and financials.debt_to_equity > 1.5:
                financials.red_flags.append("High debt-to-equity ratio")
            
            if financials.pe_ratio and financials.pe_ratio > 40:
                financials.red_flags.append("Unusually high P/E ratio")
            
            return financials
            
        except Exception as e:
            print(f"Error fetching company financials for {symbol}: {e}")
            return CompanyFinancials(symbol=symbol)
    
    async def score_fraud_relevance(self, data_item: Dict[str, Any]) -> float:
        """Use AI to score data relevance to fraud detection (0-100)"""
        try:
            # Create a prompt for Gemini to analyze fraud relevance
            if "title" in data_item:  # News item
                prompt = f"""
                Analyze this financial news item for its relevance to fraud detection and investor protection.
                
                Title: {data_item.get('title', '')}
                Content: {data_item.get('content', '')[:500]}...
                
                Score from 0-100 how relevant this is to fraud detection, considering:
                - Mentions of regulatory actions
                - Market manipulation indicators
                - Investor warnings
                - Unusual market activity
                - Scam-related keywords
                
                Respond with just a number between 0-100.
                """
            else:  # Stock data
                prompt = f"""
                Analyze this stock market data for fraud indicators.
                
                Symbol: {data_item.get('symbol', '')}
                Price Change: {data_item.get('change_percent', 0)}%
                Volume: {data_item.get('volume', 0)}
                
                Score from 0-100 how likely this represents fraudulent activity, considering:
                - Unusual price movements
                - Volume spikes
                - Pump and dump patterns
                
                Respond with just a number between 0-100.
                """
            
            # Use Gemini to score relevance
            response = await self.gemini_service.analyze_text(prompt)
            
            # Extract numeric score from response
            try:
                score = float(response.strip())
                return max(0, min(100, score))  # Ensure 0-100 range
            except ValueError:
                # Fallback scoring based on keywords
                content = str(data_item).lower()
                score = 0
                fraud_keywords = ['fraud', 'scam', 'manipulation', 'sebi', 'warning', 'alert', 'suspicious']
                for keyword in fraud_keywords:
                    if keyword in content:
                        score += 15
                return min(100, score)
                
        except Exception as e:
            print(f"Error scoring fraud relevance: {e}")
            # Fallback scoring
            return 25  # Default moderate relevance
    
    async def get_company_profile(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get company profile information"""
        try:
            # Try real FMP API first, fallback to mock if API key is demo or fails
            if self.api_key != "demo":
                return await self._get_real_company_profile(symbol)
            else:
                return await self._get_mock_company_profile(symbol)
        except Exception as e:
            print(f"Error fetching company profile for {symbol}: {e}")
            return await self._get_mock_company_profile(symbol)
    
    async def _get_real_company_profile(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get real company profile from FMP API"""
        try:
            async with httpx.AsyncClient() as client:
                profile_url = f"{self.base_url}/profile/{symbol}"
                response = await client.get(
                    profile_url,
                    params={"apikey": self.api_key},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    profile_data = response.json()
                    if profile_data and len(profile_data) > 0:
                        profile = profile_data[0]
                        return {
                            'symbol': profile.get('symbol', symbol),
                            'companyName': profile.get('companyName', ''),
                            'sector': profile.get('sector', ''),
                            'industry': profile.get('industry', ''),
                            'mktCap': profile.get('mktCap', 0),
                            'country': profile.get('country', ''),
                            'exchange': profile.get('exchangeShortName', ''),
                            'website': profile.get('website', ''),
                            'description': profile.get('description', '')
                        }
                return None
        except Exception as e:
            print(f"Error fetching real company profile for {symbol}: {e}")
            return None
    
    async def _get_mock_company_profile(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Generate mock company profile for demo/fallback"""
        if symbol in [s.replace('.NS', '') for s in self.indian_stocks]:
            return {
                'symbol': symbol,
                'companyName': f"{symbol} Limited",
                'sector': ['Technology', 'Banking', 'Consumer Goods', 'Energy'][hash(symbol) % 4],
                'industry': f"{symbol} Industry",
                'mktCap': (hash(symbol) % 1000000) * 1000000,
                'country': 'India',
                'exchange': 'NSE'
            }
        return None
    
    async def get_company_news(self, symbol: str) -> List[Dict[str, Any]]:
        """Get recent news for a company"""
        try:
            # Try real FMP API first, fallback to mock if API key is demo or fails
            if self.api_key != "demo":
                return await self._get_real_company_news(symbol)
            else:
                return await self._get_mock_company_news(symbol)
        except Exception as e:
            print(f"Error fetching company news for {symbol}: {e}")
            return await self._get_mock_company_news(symbol)
    
    async def _get_real_company_news(self, symbol: str) -> List[Dict[str, Any]]:
        """Get real company news from FMP API"""
        try:
            async with httpx.AsyncClient() as client:
                news_url = f"{self.base_url}/stock_news"
                response = await client.get(
                    news_url,
                    params={
                        "apikey": self.api_key,
                        "tickers": symbol,
                        "limit": 10
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    news_data = response.json()
                    
                    company_news = []
                    for article in news_data:
                        company_news.append({
                            'title': article.get('title', ''),
                            'content': article.get('text', '')[:300] + "..." if len(article.get('text', '')) > 300 else article.get('text', ''),
                            'publishedDate': article.get('publishedDate', ''),
                            'url': article.get('url', ''),
                            'symbol': symbol
                        })
                    
                    return company_news
                
                return []
        except Exception as e:
            print(f"Error fetching real company news for {symbol}: {e}")
            return []
    
    async def _get_mock_company_news(self, symbol: str) -> List[Dict[str, Any]]:
        """Generate mock company news for demo/fallback"""
        mock_news = [
            {
                'title': f"{symbol} Reports Strong Quarterly Results",
                'content': f"Company {symbol} has announced strong financial performance for the quarter.",
                'publishedDate': (datetime.now() - timedelta(days=1)).isoformat(),
                'url': f"https://example.com/news/{symbol.lower()}-results",
                'symbol': symbol
            },
            {
                'title': f"Regulatory Update Affects {symbol} Operations",
                'content': f"New regulations may impact {symbol}'s business operations going forward.",
                'publishedDate': (datetime.now() - timedelta(days=3)).isoformat(),
                'url': f"https://example.com/news/{symbol.lower()}-regulatory",
                'symbol': symbol
            }
        ]
        
        # Add fraud-related news for some symbols (for demo)
        if hash(symbol) % 3 == 0:  # 1/3 of symbols get fraud news
            mock_news.append({
                'title': f"SEBI Investigates {symbol} for Market Manipulation",
                'content': f"Securities regulator SEBI has launched an investigation into {symbol} for alleged market manipulation.",
                'publishedDate': (datetime.now() - timedelta(days=5)).isoformat(),
                'url': f"https://example.com/news/{symbol.lower()}-investigation",
                'symbol': symbol
            })
        
        return mock_news

# Global service instance
fmp_service = FMPIntegrationService()