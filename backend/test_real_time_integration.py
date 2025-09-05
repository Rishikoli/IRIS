#!/usr/bin/env python3
"""
Test script for real-time data integration
Tests FMP, Google Trends, and Economic Times services
"""

import asyncio
import os
import sys
from datetime import datetime

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.fmp_service import fmp_service
from app.services.google_trends_service import GoogleTrendsService
from app.services.economic_times_service import EconomicTimesScrapingService
from app.services.api_key_manager import api_key_manager
from app.services.cache_service import cache_service, rate_limit_service

async def test_fmp_service():
    """Test FMP service integration"""
    print("\n=== Testing FMP Service ===")
    
    try:
        # Test market data
        print("Fetching market data...")
        market_data = await fmp_service.fetch_market_data(["RELIANCE.NS", "TCS.NS"])
        
        if market_data:
            print(f"✓ Successfully fetched {len(market_data)} stock quotes")
            for stock in market_data[:2]:
                print(f"  {stock.symbol}: ₹{stock.price:.2f} ({stock.change_percent:+.2f}%)")
        else:
            print("✗ No market data received")
        
        # Test financial news
        print("\nFetching financial news...")
        news = await fmp_service.fetch_financial_news()
        
        if news:
            print(f"✓ Successfully fetched {len(news)} news articles")
            for article in news[:2]:
                print(f"  - {article.title[:80]}...")
        else:
            print("✗ No news data received")
        
        # Test API key status
        api_key = await api_key_manager.get_api_key("fmp")
        print(f"\nAPI Key Status: {'Real API' if api_key and api_key != 'demo' else 'Demo/Mock'}")
        
    except Exception as e:
        print(f"✗ FMP Service Error: {e}")

async def test_google_trends_service():
    """Test Google Trends service integration"""
    print("\n=== Testing Google Trends Service ===")
    
    try:
        trends_service = GoogleTrendsService()
        
        # Test fraud trends
        print("Fetching fraud trends...")
        trends = await trends_service.fetch_fraud_trends(["Mumbai", "Delhi"], "7d")
        
        if trends:
            print(f"✓ Successfully fetched {len(trends)} trend data points")
            for trend in trends[:3]:
                print(f"  {trend.keyword} in {trend.region}: {trend.search_volume} ({trend.trend_direction})")
        else:
            print("✗ No trends data received")
        
        # Test spike analysis
        print("\nAnalyzing search spikes...")
        spikes = await trends_service.analyze_search_spikes(trends)
        
        if spikes:
            print(f"✓ Detected {len(spikes)} search spikes")
            for spike in spikes[:2]:
                print(f"  {spike.keyword} in {spike.region}: {spike.spike_intensity:.1f}x normal")
        else:
            print("✓ No unusual spikes detected")
        
        print(f"\nAPI Status: {'Real API' if trends_service.use_real_api else 'Mock Data'}")
        
    except Exception as e:
        print(f"✗ Google Trends Service Error: {e}")

async def test_economic_times_service():
    """Test Economic Times scraping service"""
    print("\n=== Testing Economic Times Service ===")
    
    try:
        et_service = EconomicTimesScrapingService()
        
        # Test news scraping
        print("Scraping latest news...")
        articles = await et_service.scrape_latest_news(["markets"])
        
        if articles:
            print(f"✓ Successfully scraped {len(articles)} articles")
            for article in articles[:2]:
                print(f"  - {article.title[:80]}...")
                print(f"    Fraud relevance: {article.fraud_relevance_score:.1f}/100")
        else:
            print("✗ No articles scraped")
        
        # Test market sentiment
        print("\nAnalyzing market sentiment...")
        sentiment = await et_service.extract_market_sentiment(articles)
        
        print(f"✓ Market sentiment: {sentiment.overall_sentiment} ({sentiment.confidence_score:.1f}% confidence)")
        if sentiment.key_themes:
            print(f"  Key themes: {', '.join(sentiment.key_themes)}")
        
        print(f"\nScraping Status: {'Real Scraping' if et_service.use_real_scraping else 'Mock Data'}")
        
    except Exception as e:
        print(f"✗ Economic Times Service Error: {e}")

async def test_cache_and_rate_limiting():
    """Test caching and rate limiting functionality"""
    print("\n=== Testing Cache and Rate Limiting ===")
    
    try:
        # Test cache
        print("Testing cache functionality...")
        test_key = "test_key"
        test_data = {"message": "test data", "timestamp": datetime.now().isoformat()}
        
        # Set cache
        success = await cache_service.set(test_key, test_data, 60, "test")
        print(f"Cache set: {'✓' if success else '✗'}")
        
        # Get cache
        cached_data = await cache_service.get(test_key)
        print(f"Cache get: {'✓' if cached_data else '✗'}")
        
        # Test rate limiting
        print("\nTesting rate limiting...")
        for i in range(3):
            allowed = await rate_limit_service.check_rate_limit("test_service", "test_user")
            print(f"Rate limit check {i+1}: {'✓' if allowed else '✗'}")
        
        # Get rate limit status
        status = await rate_limit_service.get_rate_limit_status("test_service", "test_user")
        print(f"Rate limit status: {status['requests_made']}/{status['limit']} requests")
        
    except Exception as e:
        print(f"✗ Cache/Rate Limiting Error: {e}")

async def test_api_key_management():
    """Test API key management functionality"""
    print("\n=== Testing API Key Management ===")
    
    try:
        # Test service health
        services = ["fmp", "gemini", "trends"]
        
        for service in services:
            health = await api_key_manager.get_service_health(service)
            available = await api_key_manager.is_service_available(service)
            
            print(f"{service.upper()} Service:")
            print(f"  Available: {'✓' if available else '✗'}")
            if health:
                print(f"  Status: {health.status}")
                print(f"  Response time: {health.response_time_ms:.1f}ms")
            
            # Test usage stats
            usage = await api_key_manager.get_usage_stats(service)
            print(f"  Usage: {usage['primary_key']['daily_usage']} requests today")
        
    except Exception as e:
        print(f"✗ API Key Management Error: {e}")

async def main():
    """Run all tests"""
    print("IRIS RegTech Platform - Real-Time Data Integration Test")
    print("=" * 60)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"FMP API: {'Enabled' if os.getenv('USE_REAL_FMP', 'false').lower() == 'true' else 'Mock'}")
    print(f"Google Trends: {'Enabled' if os.getenv('USE_REAL_TRENDS', 'false').lower() == 'true' else 'Mock'}")
    print(f"Economic Times: {'Enabled' if os.getenv('USE_REAL_SCRAPING', 'false').lower() == 'true' else 'Mock'}")
    
    # Run tests
    await test_cache_and_rate_limiting()
    await test_api_key_management()
    await test_fmp_service()
    await test_google_trends_service()
    await test_economic_times_service()
    
    print("\n" + "=" * 60)
    print("Test completed!")
    
    # Provide configuration recommendations
    print("\n📋 Configuration Recommendations:")
    
    if os.getenv("FMP_API_KEY", "demo") == "demo":
        print("• Get a real FMP API key from https://financialmodelingprep.com/")
        print("• Set FMP_API_KEY in your .env file")
        print("• Set USE_REAL_FMP=true to enable real market data")
    
    if os.getenv("USE_REAL_TRENDS", "false").lower() != "true":
        print("• Set USE_REAL_TRENDS=true to enable real Google Trends data")
        print("• Note: Google Trends has strict rate limits")
    
    if os.getenv("USE_REAL_SCRAPING", "false").lower() != "true":
        print("• Set USE_REAL_SCRAPING=true to enable real Economic Times scraping")
        print("• Be respectful of website rate limits")
    
    if not os.getenv("REDIS_URL"):
        print("• Install and configure Redis for better caching performance")
        print("• Set REDIS_URL=redis://localhost:6379 in your .env file")

if __name__ == "__main__":
    asyncio.run(main())