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
        """Scrape latest financial news from Economic Times"""
        if not categories:
            categories = ["markets", "policy"]
        
        try:
            if self.use_real_scraping:
                return await self._scrape_real_news(categories)
            else:
                return await self._generate_mock_news()
            
        except Exception as e:
            print(f"Error scraping news: {e}")
            return await self._generate_mock_news()
    
    async def _scrape_real_news(self, categories: List[str]) -> List[NewsArticle]:
        """Scrape real news from Economic Times website"""
        articles = []
        
        async with httpx.AsyncClient(headers=self.headers, timeout=30.0) as client:
            for category in categories:
                try:
                    category_url = self.base_url + self.categories.get(category, "/markets")
                    
                    response = await client.get(category_url)
                    if response.status_code != 200:
                        continue
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Find article links (Economic Times specific selectors)
                    article_links = soup.find_all('a', href=True)
                    
                    for link in article_links[:10]:  # Limit to 10 articles per category
                        href = link.get('href')
                        if not href or not href.startswith('/'):
                            continue
                        
                        article_url = self.base_url + href
                        title_element = link.find('h3') or link.find('h2') or link
                        title = title_element.get_text(strip=True) if title_element else ""
                        
                        # Filter for relevant articles
                        if not title or len(title) < 20:
                            continue
                        
                        # Check if article is fraud/regulatory related
                        title_lower = title.lower()
                        is_relevant = (
                            any(keyword in title_lower for keyword in self.fraud_keywords) or
                            any(regulator.lower() in title_lower for regulator in self.regulators)
                        )
                        
                        if is_relevant:
                            # Scrape full article content
                            article_content = await self._scrape_article_content(client, article_url)
                            
                            if article_content:
                                # Extract regulatory mentions and stock mentions
                                regulatory_mentions = [reg for reg in self.regulators if reg.lower() in article_content.lower()]
                                stock_mentions = self._extract_stock_mentions(article_content)
                                
                                # Calculate fraud relevance score
                                fraud_score = self._calculate_fraud_relevance(title, article_content)
                                
                                article = NewsArticle(
                                    title=title,
                                    content=article_content[:1000] + "..." if len(article_content) > 1000 else article_content,
                                    url=article_url,
                                    category=category,
                                    published_at=datetime.now() - timedelta(hours=random.randint(1, 24)),
                                    fraud_relevance_score=fraud_score,
                                    regulatory_mentions=regulatory_mentions,
                                    stock_mentions=stock_mentions,
                                    sentiment=self._analyze_sentiment(title + " " + article_content)
                                )
                                articles.append(article)
                        
                        # Add delay to be respectful to the website
                        await asyncio.sleep(0.5)
                        
                        if len(articles) >= 20:  # Limit total articles
                            break
                    
                except Exception as e:
                    print(f"Error scraping category {category}: {e}")
                    continue
        
        return articles
    
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