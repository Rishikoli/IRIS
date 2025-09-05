"""
Economic Times Web Scraping Service
Scrapes Indian financial news for fraud-related content and regulatory updates
"""

import asyncio
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
import re
import os
import random
from app.services.gemini_service import GeminiService
from app.services.cache_service import cache_service, rate_limit_service, data_freshness_service

class NewsArticle(BaseModel):
    title: str
    content: str
    url: str
    category: str
    author: Optional[str] = None
    published_at: datetime
    fraud_relevance_score: float = 0.0
    sentiment: str = "neutral"
    regulatory_mentions: List[str] = []
    stock_mentions: List[str] = []

class RegulatoryUpdate(BaseModel):
    title: str
    content: str
    regulator: str  # SEBI, RBI, IRDAI, etc.
    update_type: str  # guideline, warning, action, etc.
    published_at: datetime
    impact_level: str  # high, medium, low
    affected_sectors: List[str] = []

class MarketSentiment(BaseModel):
    overall_sentiment: str  # positive, negative, neutral
    confidence_score: float  # 0-100
    key_themes: List[str]
    fraud_risk_indicators: List[str]
    regulatory_activity_level: str  # high, medium, low

class EconomicTimesScrapingService:
    def __init__(self):
        self.base_url = "https://economictimes.indiatimes.com"
        self.gemini_service = GeminiService()
        self.use_real_scraping = os.getenv("USE_REAL_SCRAPING", "false").lower() == "true"
        
        # Rate limiting and retry configuration
        self.scraping_delay = float(os.getenv("SCRAPING_DELAY_SECONDS", "1"))
        self.max_retries = 3
        self.retry_delay = 2.0
        
        # Cache TTL settings (in seconds)
        self.cache_ttl = {
            "news_articles": 1800,    # 30 minutes
            "regulatory_updates": 3600, # 1 hour
            "market_sentiment": 900    # 15 minutes
        }
        
        # Categories to monitor
        self.categories = {
            "markets": "/markets",
            "policy": "/news/economy/policy",
            "banking": "/industry/banking/finance"
        }
        
        # Regulatory bodies to track
        self.regulators = ["SEBI", "RBI", "IRDAI", "NPCI", "MCA"]
        
        # Fraud-related keywords
        self.fraud_keywords = [
            "fraud", "scam", "manipulation", "ponzi", "chit fund",
            "fake", "illegal", "unauthorized", "warning", "alert",
            "investigation", "enforcement", "penalty", "action"
        ]
        
        # Headers for web scraping
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
    
    async def scrape_latest_news(self, categories: Optional[List[str]] = None) -> List[NewsArticle]:
        """Scrape latest financial news from Economic Times with caching and rate limiting"""
        if not categories:
            categories = ["markets", "policy"]
        
        # Generate cache key
        cache_key = cache_service.generate_cache_key("economic_times", "news", {"categories": categories})
        
        # Try to get from cache first
        cached_data = await cache_service.get(cache_key)
        if cached_data and await data_freshness_service.is_data_fresh("news_data", cache_key):
            return [NewsArticle(**item) for item in cached_data]
        
        try:
            # Check rate limit
            if not await rate_limit_service.check_rate_limit("scraping"):
                print("Economic Times scraping rate limit exceeded, using cached data")
                if cached_data:
                    return [NewsArticle(**item) for item in cached_data]
                else:
                    return await self._generate_mock_news()
            
            # Fetch real data if scraping is enabled
            if self.use_real_scraping:
                data = await self._scrape_real_news_with_retry(categories)
            else:
                data = await self._generate_mock_news()
            
            # Cache the results
            serializable_data = [item.model_dump() for item in data]
            await cache_service.set(cache_key, serializable_data, self.cache_ttl["news_articles"], "economic_times")
            await data_freshness_service.mark_data_fresh("news_data", cache_key, "economic_times")
            
            return data
            
        except Exception as e:
            print(f"Error scraping news: {e}")
            # Fallback to cached data or mock data
            if cached_data:
                return [NewsArticle(**item) for item in cached_data]
            return await self._generate_mock_news()
    
    async def _scrape_real_news_with_retry(self, categories: List[str]) -> List[NewsArticle]:
        """Scrape real news with retry logic"""
        for attempt in range(self.max_retries):
            try:
                return await self._scrape_real_news(categories)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise e
                print(f"Scraping attempt {attempt + 1} failed, retrying: {e}")
                await asyncio.sleep(self.retry_delay * (attempt + 1))
        
        return []
    
    async def _scrape_real_news(self, categories: List[str]) -> List[NewsArticle]:
        """Scrape real news from Economic Times website"""
        articles = []
        
        async with httpx.AsyncClient(headers=self.headers, timeout=30.0, follow_redirects=True) as client:
            for category in categories:
                try:
                    category_url = self.base_url + self.categories.get(category, "/markets")
                    
                    response = await client.get(category_url)
                    if response.status_code != 200:
                        print(f"Failed to fetch {category_url}: {response.status_code}")
                        continue
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Enhanced selectors for Economic Times
                    article_selectors = [
                        'a[href*="/news/"]',
                        'a[href*="/markets/"]',
                        'a[href*="/industry/"]',
                        '.eachStory a',
                        '.story-box a',
                        'h3 a',
                        'h2 a'
                    ]
                    
                    found_links = []
                    for selector in article_selectors:
                        links = soup.select(selector)
                        found_links.extend(links)
                    
                    # Remove duplicates
                    unique_links = {}
                    for link in found_links:
                        href = link.get('href')
                        if href and href not in unique_links:
                            unique_links[href] = link
                    
                    processed_count = 0
                    for href, link in unique_links.items():
                        if processed_count >= 15:  # Limit per category
                            break
                        
                        # Normalize URL
                        if href.startswith('/'):
                            article_url = self.base_url + href
                        elif href.startswith('http'):
                            article_url = href
                        else:
                            continue
                        
                        # Extract title
                        title = link.get_text(strip=True)
                        if not title:
                            title_elem = link.find(['h1', 'h2', 'h3', 'h4'])
                            title = title_elem.get_text(strip=True) if title_elem else ""
                        
                        # Filter for relevant articles
                        if not title or len(title) < 15:
                            continue
                        
                        # Enhanced relevance checking
                        title_lower = title.lower()
                        is_fraud_related = any(keyword in title_lower for keyword in self.fraud_keywords)
                        is_regulatory_related = any(regulator.lower() in title_lower for regulator in self.regulators)
                        is_market_related = any(keyword in title_lower for keyword in [
                            'stock', 'market', 'trading', 'investment', 'investor', 'share', 'equity'
                        ])
                        
                        if is_fraud_related or is_regulatory_related or (is_market_related and category == "markets"):
                            try:
                                # Add delay to be respectful
                                await asyncio.sleep(self.scraping_delay)
                                
                                # Scrape full article content
                                article_content = await self._scrape_article_content_enhanced(client, article_url)
                                
                                if article_content and len(article_content) > 50:
                                    # Extract regulatory mentions and stock mentions
                                    regulatory_mentions = [
                                        reg for reg in self.regulators 
                                        if reg.lower() in (title + " " + article_content).lower()
                                    ]
                                    stock_mentions = self._extract_stock_mentions(title + " " + article_content)
                                    
                                    # Calculate fraud relevance score
                                    fraud_score = self._calculate_fraud_relevance(title, article_content)
                                    
                                    # Determine sentiment
                                    sentiment = self._analyze_sentiment(title + " " + article_content)
                                    
                                    article = NewsArticle(
                                        title=title,
                                        content=article_content[:1200] + "..." if len(article_content) > 1200 else article_content,
                                        url=article_url,
                                        category=category,
                                        published_at=datetime.now() - timedelta(hours=random.randint(1, 48)),
                                        fraud_relevance_score=fraud_score,
                                        regulatory_mentions=regulatory_mentions,
                                        stock_mentions=stock_mentions,
                                        sentiment=sentiment
                                    )
                                    articles.append(article)
                                    processed_count += 1
                                
                            except Exception as e:
                                print(f"Error processing article {article_url}: {e}")
                                continue
                        
                        if len(articles) >= 25:  # Global limit
                            break
                    
                except Exception as e:
                    print(f"Error scraping category {category}: {e}")
                    continue
        
        return articles
    
    async def _scrape_article_content_enhanced(self, client: httpx.AsyncClient, url: str) -> Optional[str]:
        """Enhanced article content scraping with better selectors"""
        try:
            response = await client.get(url, timeout=15.0)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Enhanced content selectors for Economic Times
            content_selectors = [
                '.artText',
                '.Normal',
                '.story-content',
                'div[data-module="ArticleContent"]',
                '.article-content',
                '.articleBody',
                '.story_content',
                '.content-wrapper p',
                'article p',
                '.main-content p'
            ]
            
            content = ""
            for selector in content_selectors:
                content_elements = soup.select(selector)
                if content_elements:
                    content = " ".join([elem.get_text(strip=True) for elem in content_elements])
                    if len(content) > 100:  # Ensure we got substantial content
                        break
            
            # Fallback: get all paragraph text if specific selectors fail
            if not content or len(content) < 100:
                paragraphs = soup.find_all('p')
                content = " ".join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20])
            
            # Clean up content
            if content:
                # Remove extra whitespace
                content = re.sub(r'\s+', ' ', content)
                # Remove common footer text
                content = re.sub(r'(Subscribe to|Follow us on|Download the app).*$', '', content, flags=re.IGNORECASE)
                
            return content[:2500] if content else None  # Limit content length
            
        except Exception as e:
            print(f"Error scraping article content from {url}: {e}")
            return None
    
    async def _scrape_article_content(self, client: httpx.AsyncClient, url: str) -> Optional[str]:
        """Scrape full content of an article"""
        try:
            response = await client.get(url)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Economic Times specific content selectors
            content_selectors = [
                '.artText',
                '.Normal',
                '.story-content',
                'div[data-module="ArticleContent"]',
                '.article-content'
            ]
            
            content = ""
            for selector in content_selectors:
                content_elements = soup.select(selector)
                if content_elements:
                    content = " ".join([elem.get_text(strip=True) for elem in content_elements])
                    break
            
            # Fallback: get all paragraph text
            if not content:
                paragraphs = soup.find_all('p')
                content = " ".join([p.get_text(strip=True) for p in paragraphs])
            
            return content[:2000] if content else None  # Limit content length
            
        except Exception as e:
            print(f"Error scraping article content from {url}: {e}")
            return None
    
    def _extract_stock_mentions(self, text: str) -> List[str]:
        """Extract stock symbols mentioned in the text"""
        # Common Indian stock symbols pattern
        stock_pattern = r'\b[A-Z]{2,6}(?:\.NS|\.BO)?\b'
        potential_stocks = re.findall(stock_pattern, text)
        
        # Filter out common false positives
        excluded = {'SEBI', 'RBI', 'IRDAI', 'NPCI', 'MCA', 'CEO', 'CFO', 'IPO', 'FPO', 'NSE', 'BSE'}
        return [stock for stock in potential_stocks if stock not in excluded]
    
    def _calculate_fraud_relevance(self, title: str, content: str) -> float:
        """Calculate fraud relevance score (0-100)"""
        text = (title + " " + content).lower()
        
        score = 0
        for keyword in self.fraud_keywords:
            if keyword in text:
                score += 15
        
        for regulator in self.regulators:
            if regulator.lower() in text:
                score += 10
        
        return min(100, score)
    
    def _analyze_sentiment(self, text: str) -> str:
        """Simple sentiment analysis"""
        text_lower = text.lower()
        
        positive_words = ['growth', 'profit', 'gain', 'rise', 'surge', 'strong', 'positive', 'success']
        negative_words = ['fraud', 'scam', 'loss', 'fall', 'decline', 'warning', 'penalty', 'investigation']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if negative_count > positive_count:
            return "negative"
        elif positive_count > negative_count:
            return "positive"
        else:
            return "neutral"
    
    async def _generate_mock_news(self) -> List[NewsArticle]:
        """Generate mock news articles for demo/fallback"""
        try:
            mock_articles = [
                NewsArticle(
                    title="SEBI Cracks Down on Unauthorized Investment Advisors",
                    content="The Securities and Exchange Board of India has initiated action against several unauthorized investment advisors who were operating without proper registration. The regulator found that these entities were providing investment advice through social media platforms and messaging apps, targeting retail investors with promises of guaranteed returns.",
                    url="https://economictimes.indiatimes.com/markets/stocks/news/sebi-cracks-down-unauthorized-advisors",
                    category="markets",
                    author="ET Bureau",
                    published_at=datetime.now() - timedelta(hours=2),
                    regulatory_mentions=["SEBI"],
                    stock_mentions=[]
                ),
                NewsArticle(
                    title="RBI Issues Warning Against Fraudulent Loan Apps",
                    content="The Reserve Bank of India has issued a public warning against fraudulent digital lending applications that are charging excessive interest rates and using unethical recovery practices. The central bank advised consumers to verify the credentials of lending platforms before availing services.",
                    url="https://economictimes.indiatimes.com/industry/banking/finance/rbi-warning-fraudulent-loan-apps",
                    category="banking",
                    author="Mayur Shetty",
                    published_at=datetime.now() - timedelta(hours=4),
                    regulatory_mentions=["RBI"],
                    stock_mentions=[]
                ),
                NewsArticle(
                    title="Tech Stocks Rally on AI Investment Announcements",
                    content="Indian technology stocks surged in today's trading session following major announcements about artificial intelligence investments by leading IT companies. TCS, Infosys, and HCL Technologies led the gains as investors showed confidence in the sector's AI capabilities.",
                    url="https://economictimes.indiatimes.com/markets/stocks/news/tech-stocks-rally-ai-investments",
                    category="markets",
                    author="Kshitij Anand",
                    published_at=datetime.now() - timedelta(hours=6),
                    regulatory_mentions=[],
                    stock_mentions=["TCS", "INFY", "HCLTECH"]
                ),
                NewsArticle(
                    title="Banking Sector Faces Increased Scrutiny Over Digital Lending",
                    content="The banking sector is under increased regulatory scrutiny following reports of aggressive lending practices by fintech companies. SEBI and RBI are working together to establish clearer guidelines for digital lending platforms to protect consumer interests.",
                    url="https://economictimes.indiatimes.com/industry/banking/finance/banking-sector-digital-lending-scrutiny",
                    category="banking",
                    author="Sangita Mehta",
                    published_at=datetime.now() - timedelta(hours=8),
                    regulatory_mentions=["SEBI", "RBI"],
                    stock_mentions=["HDFCBANK", "ICICIBANK"]
                )
            ]
            
            # Score fraud relevance for each article
            for article in mock_articles:
                article.fraud_relevance_score = await self._score_fraud_relevance(article)
                article.sentiment = await self._analyze_sentiment(article)
            
            return mock_articles
            
        except Exception as e:
            print(f"Error scraping Economic Times: {e}")
            return []
    
    async def monitor_regulatory_updates(self) -> List[RegulatoryUpdate]:
        """Monitor SEBI and RBI updates from Economic Times"""
        try:
            # Mock regulatory updates for demo
            mock_updates = [
                RegulatoryUpdate(
                    title="SEBI Introduces New KYC Norms for Investment Advisors",
                    content="SEBI has introduced enhanced Know Your Customer (KYC) norms for investment advisors to prevent fraudulent activities. The new guidelines require additional verification steps and regular compliance reporting.",
                    regulator="SEBI",
                    update_type="guideline",
                    published_at=datetime.now() - timedelta(hours=3),
                    impact_level="high",
                    affected_sectors=["Financial Services", "Investment Advisory"]
                ),
                RegulatoryUpdate(
                    title="RBI Mandates Additional Security for Digital Payments",
                    content="The Reserve Bank of India has mandated additional security measures for digital payment platforms following an increase in payment fraud cases. New authentication protocols will be implemented within 90 days.",
                    regulator="RBI",
                    update_type="mandate",
                    published_at=datetime.now() - timedelta(hours=5),
                    impact_level="medium",
                    affected_sectors=["Banking", "Fintech", "Payments"]
                )
            ]
            
            return mock_updates
            
        except Exception as e:
            print(f"Error monitoring regulatory updates: {e}")
            return []
    
    async def extract_market_sentiment(self, articles: List[NewsArticle]) -> MarketSentiment:
        """Extract overall market sentiment from scraped articles"""
        try:
            if not articles:
                return MarketSentiment(
                    overall_sentiment="neutral",
                    confidence_score=0.0,
                    key_themes=[],
                    fraud_risk_indicators=[],
                    regulatory_activity_level="low"
                )
            
            # Analyze sentiment distribution
            sentiments = [article.sentiment for article in articles]
            positive_count = sentiments.count("positive")
            negative_count = sentiments.count("negative")
            neutral_count = sentiments.count("neutral")
            
            total_articles = len(articles)
            
            # Determine overall sentiment
            if positive_count > negative_count and positive_count > neutral_count:
                overall_sentiment = "positive"
                confidence = (positive_count / total_articles) * 100
            elif negative_count > positive_count and negative_count > neutral_count:
                overall_sentiment = "negative"
                confidence = (negative_count / total_articles) * 100
            else:
                overall_sentiment = "neutral"
                confidence = (neutral_count / total_articles) * 100
            
            # Extract key themes
            key_themes = []
            fraud_indicators = []
            
            for article in articles:
                # Extract themes from titles
                if any(keyword in article.title.lower() for keyword in ["ai", "technology", "tech"]):
                    key_themes.append("Technology Growth")
                if any(keyword in article.title.lower() for keyword in ["banking", "finance"]):
                    key_themes.append("Financial Sector")
                if any(keyword in article.title.lower() for keyword in ["regulation", "sebi", "rbi"]):
                    key_themes.append("Regulatory Activity")
                
                # Extract fraud indicators
                if article.fraud_relevance_score > 70:
                    fraud_indicators.append(f"High fraud risk in {article.category}")
                elif any(keyword in article.content.lower() for keyword in self.fraud_keywords):
                    fraud_indicators.append("Fraud-related news activity")
            
            # Remove duplicates
            key_themes = list(set(key_themes))
            fraud_indicators = list(set(fraud_indicators))
            
            # Determine regulatory activity level
            regulatory_mentions = sum(len(article.regulatory_mentions) for article in articles)
            if regulatory_mentions > 5:
                regulatory_activity_level = "high"
            elif regulatory_mentions > 2:
                regulatory_activity_level = "medium"
            else:
                regulatory_activity_level = "low"
            
            return MarketSentiment(
                overall_sentiment=overall_sentiment,
                confidence_score=confidence,
                key_themes=key_themes,
                fraud_risk_indicators=fraud_indicators,
                regulatory_activity_level=regulatory_activity_level
            )
            
        except Exception as e:
            print(f"Error extracting market sentiment: {e}")
            return MarketSentiment(
                overall_sentiment="neutral",
                confidence_score=0.0,
                key_themes=[],
                fraud_risk_indicators=[],
                regulatory_activity_level="low"
            )
    
    async def _score_fraud_relevance(self, article: NewsArticle) -> float:
        """Score article relevance to fraud detection using AI"""
        try:
            prompt = f"""
            Analyze this financial news article for fraud relevance:
            
            Title: {article.title}
            Content: {article.content[:500]}...
            Category: {article.category}
            Regulatory Mentions: {', '.join(article.regulatory_mentions)}
            
            Score from 0-100 how relevant this article is to fraud detection and investor protection, considering:
            - Regulatory actions or warnings
            - Fraud investigations or cases
            - Market manipulation indicators
            - Investor protection measures
            - Scam-related content
            
            Respond with just a number between 0-100.
            """
            
            response = await self.gemini_service.analyze_text(prompt)
            
            try:
                score = float(response.strip())
                return max(0, min(100, score))
            except ValueError:
                # Fallback scoring based on keywords
                content_lower = (article.title + " " + article.content).lower()
                score = 0
                
                for keyword in self.fraud_keywords:
                    if keyword in content_lower:
                        score += 10
                
                if article.regulatory_mentions:
                    score += len(article.regulatory_mentions) * 15
                
                return min(100, score)
                
        except Exception as e:
            print(f"Error scoring fraud relevance: {e}")
            return 25.0  # Default moderate relevance
    
    async def _analyze_sentiment(self, article: NewsArticle) -> str:
        """Analyze article sentiment using AI"""
        try:
            prompt = f"""
            Analyze the sentiment of this financial news article:
            
            Title: {article.title}
            Content: {article.content[:300]}...
            
            Classify the sentiment as one of: positive, negative, neutral
            
            Consider:
            - Market impact (positive/negative for investors)
            - Regulatory tone (supportive/restrictive)
            - Overall market confidence
            
            Respond with just one word: positive, negative, or neutral.
            """
            
            response = await self.gemini_service.analyze_text(prompt)
            sentiment = response.strip().lower()
            
            if sentiment in ["positive", "negative", "neutral"]:
                return sentiment
            else:
                return "neutral"
                
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return "neutral"
    
    async def get_fraud_related_articles(self, days_back: int = 7) -> List[NewsArticle]:
        """Get articles specifically related to fraud from the last N days"""
        try:
            all_articles = await self.scrape_latest_news()
            
            # Filter for fraud-related articles
            fraud_articles = []
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            for article in all_articles:
                if (article.published_at >= cutoff_date and 
                    article.fraud_relevance_score > 50):
                    fraud_articles.append(article)
            
            # Sort by fraud relevance score
            fraud_articles.sort(key=lambda x: x.fraud_relevance_score, reverse=True)
            
            return fraud_articles
            
        except Exception as e:
            print(f"Error getting fraud-related articles: {e}")
            return []