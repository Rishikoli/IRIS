# Real-Time Data Integration Guide

This document explains the real-time data integration implementation for the IRIS RegTech platform, including setup, configuration, and usage.

## Overview

The IRIS platform integrates with multiple real-time data sources to provide comprehensive fraud detection and market monitoring:

1. **Financial Modeling Prep (FMP) API** - Real-time stock data and financial news
2. **Google Trends API** - Fraud-related search trend analysis
3. **Economic Times Web Scraping** - Indian financial news and regulatory updates
4. **Caching & Rate Limiting** - Performance optimization and API quota management

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI        │    │   External APIs │
│   Dashboard     │◄──►│   Backend        │◄──►│   & Services    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   Cache Layer    │
                       │   (Redis/Memory) │
                       └──────────────────┘
```

## Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory with the following configuration:

```bash
# API Keys
FMP_API_KEY=your_fmp_api_key_here
FMP_API_KEY_FALLBACK=backup_key_optional
GEMINI_API_KEY=your_gemini_api_key_here

# Feature Flags
USE_REAL_FMP=true
USE_REAL_TRENDS=true
USE_REAL_SCRAPING=true

# Rate Limiting
FMP_RATE_LIMIT_PER_MINUTE=60
TRENDS_RATE_LIMIT_PER_HOUR=100
SCRAPING_DELAY_SECONDS=2

# Caching
REDIS_URL=redis://localhost:6379
CACHE_TTL_SECONDS=300

# Environment
ENVIRONMENT=production
```

### API Key Setup

#### 1. Financial Modeling Prep (FMP)

1. Sign up at [https://financialmodelingprep.com/](https://financialmodelingprep.com/)
2. Get your API key from the dashboard
3. Set `FMP_API_KEY` in your `.env` file
4. Set `USE_REAL_FMP=true`

**Free Tier Limits:**
- 250 requests per day
- Real-time quotes for major exchanges
- Historical data access

**Paid Tiers:**
- Up to 10,000+ requests per day
- Extended market coverage
- Premium data feeds

#### 2. Google Trends (pytrends)

Google Trends doesn't require an API key but has strict rate limits:

1. Install pytrends: `pip install pytrends` (already included)
2. Set `USE_REAL_TRENDS=true`
3. Configure rate limiting: `TRENDS_RATE_LIMIT_PER_HOUR=100`

**Rate Limits:**
- ~100 requests per hour per IP
- Automatic IP blocking if exceeded
- Use caching to minimize requests

#### 3. Economic Times Scraping

Web scraping doesn't require API keys but should be used responsibly:

1. Set `USE_REAL_SCRAPING=true`
2. Configure delay: `SCRAPING_DELAY_SECONDS=2`
3. Monitor for rate limiting or blocking

**Best Practices:**
- Respect robots.txt
- Use reasonable delays between requests
- Cache results to minimize scraping
- Monitor for IP blocking

## Services Overview

### 1. FMP Integration Service

**File:** `app/services/fmp_service.py`

**Features:**
- Real-time stock quotes for Indian markets (NSE/BSE)
- Financial news with fraud relevance scoring
- Company profiles and financial data
- Automatic fallback to mock data

**Usage:**
```python
from app.services.fmp_service import fmp_service

# Get market data
market_data = await fmp_service.fetch_market_data(["RELIANCE.NS", "TCS.NS"])

# Get financial news
news = await fmp_service.fetch_financial_news()

# Get company profile
profile = await fmp_service.get_company_profile("RELIANCE.NS")
```

### 2. Google Trends Service

**File:** `app/services/google_trends_service.py`

**Features:**
- Fraud-related keyword monitoring by region
- Search spike detection
- Trend correlation with fraud cases
- Regional analysis for Indian states/cities

**Usage:**
```python
from app.services.google_trends_service import GoogleTrendsService

trends_service = GoogleTrendsService()

# Get fraud trends
trends = await trends_service.fetch_fraud_trends(["Mumbai", "Delhi"], "7d")

# Analyze spikes
spikes = await trends_service.analyze_search_spikes(trends)
```

### 3. Economic Times Scraping Service

**File:** `app/services/economic_times_service.py`

**Features:**
- Real-time financial news scraping
- Regulatory update monitoring
- Market sentiment analysis
- Fraud relevance scoring

**Usage:**
```python
from app.services.economic_times_service import EconomicTimesScrapingService

et_service = EconomicTimesScrapingService()

# Scrape latest news
articles = await et_service.scrape_latest_news(["markets", "policy"])

# Get market sentiment
sentiment = await et_service.extract_market_sentiment(articles)
```

### 4. Cache Service

**File:** `app/services/cache_service.py`

**Features:**
- Redis and in-memory caching
- Automatic cache invalidation
- Data freshness tracking
- Rate limiting implementation

**Usage:**
```python
from app.services.cache_service import cache_service

# Cache data
await cache_service.set("key", data, ttl_seconds=300)

# Retrieve data
cached_data = await cache_service.get("key")
```

### 5. API Key Manager

**File:** `app/services/api_key_manager.py`

**Features:**
- API key rotation and fallback
- Service health monitoring
- Usage tracking and quota management
- Automatic error recovery

**Usage:**
```python
from app.services.api_key_manager import api_key_manager

# Get API key
api_key = await api_key_manager.get_api_key("fmp")

# Record success/error
await api_key_manager.record_api_success("fmp", response_time_ms=150)
await api_key_manager.record_api_error("fmp", error="Rate limit exceeded")
```

## Data Flow

### 1. Request Flow

```
User Request → Cache Check → Rate Limit Check → API Call → Cache Store → Response
```

### 2. Fallback Strategy

```
Real API → Cached Data → Mock Data → Error Response
```

### 3. Error Handling

```
API Error → Log Error → Update Health Status → Try Fallback → Return Best Available Data
```

## Monitoring and Health Checks

### Data Status Endpoints

The platform provides comprehensive monitoring through the `/api/data-status` endpoints:

```bash
# Get service health
GET /api/data-status/health

# Get data quality metrics
GET /api/data-status/quality

# Get usage statistics
GET /api/data-status/usage/fmp

# Reset service health
POST /api/data-status/reset/fmp

# Get cache statistics
GET /api/data-status/cache/stats

# Get configuration
GET /api/data-status/config
```

### Health Status Levels

- **Healthy**: Service operating normally
- **Degraded**: Some errors but still functional
- **Down**: Service unavailable, using fallbacks
- **Mock**: Using mock data (development/fallback)

## Testing

### Run Integration Tests

```bash
cd backend
python test_real_time_integration.py
```

This will test:
- FMP API integration
- Google Trends functionality
- Economic Times scraping
- Cache and rate limiting
- API key management

### Manual Testing

```bash
# Test individual services
curl http://localhost:8000/api/data-status/health
curl http://localhost:8000/api/data-status/quality
curl http://localhost:8000/api/data-status/config
```

## Performance Optimization

### Caching Strategy

1. **Market Data**: 5-minute cache (real-time needs)
2. **News Data**: 30-minute cache (less frequent updates)
3. **Trends Data**: 1-hour cache (daily patterns)
4. **Company Profiles**: 24-hour cache (static data)

### Rate Limiting

1. **FMP API**: 60 requests/minute (configurable)
2. **Google Trends**: 100 requests/hour (strict limit)
3. **Web Scraping**: 1 request/second (respectful)

### Memory Management

- Automatic cache cleanup for expired entries
- Memory usage monitoring
- Redis fallback for production environments

## Production Deployment

### Prerequisites

1. **Redis Server**
   ```bash
   # Install Redis
   sudo apt-get install redis-server
   
   # Start Redis
   sudo systemctl start redis-server
   ```

2. **API Keys**
   - Obtain production API keys
   - Set up fallback keys for redundancy
   - Configure rate limits appropriately

3. **Environment Configuration**
   ```bash
   ENVIRONMENT=production
   USE_REAL_FMP=true
   USE_REAL_TRENDS=true
   USE_REAL_SCRAPING=true
   REDIS_URL=redis://localhost:6379
   ```

### Monitoring Setup

1. **Health Checks**
   - Set up automated health monitoring
   - Configure alerts for service degradation
   - Monitor API usage and quotas

2. **Logging**
   ```bash
   LOG_LEVEL=INFO
   ENABLE_METRICS=true
   ```

3. **Performance Metrics**
   - Response time monitoring
   - Cache hit rates
   - Error rates and patterns

## Troubleshooting

### Common Issues

1. **Rate Limit Exceeded**
   - Check current usage: `GET /api/data-status/usage/fmp`
   - Increase cache TTL to reduce API calls
   - Implement request queuing

2. **API Key Invalid**
   - Verify API key in service dashboard
   - Check key permissions and quotas
   - Test with fallback key

3. **Cache Issues**
   - Check Redis connection
   - Verify cache configuration
   - Clear cache if corrupted: `DELETE /api/data-status/cache/clear`

4. **Scraping Blocked**
   - Increase delay between requests
   - Rotate user agents
   - Use proxy servers if necessary

### Debug Mode

Enable debug logging:
```bash
LOG_LEVEL=DEBUG
```

Check service status:
```bash
curl http://localhost:8000/api/data-status/health | jq
```

### Recovery Procedures

1. **Service Recovery**
   ```bash
   # Reset service health
   curl -X POST http://localhost:8000/api/data-status/reset/fmp
   ```

2. **Cache Recovery**
   ```bash
   # Clear corrupted cache
   curl -X DELETE http://localhost:8000/api/data-status/cache/clear
   ```

3. **Manual Fallback**
   - Set `USE_REAL_*=false` to use mock data
   - Restart services
   - Monitor for recovery

## Security Considerations

1. **API Key Protection**
   - Store keys in environment variables
   - Use key rotation
   - Monitor for unauthorized usage

2. **Rate Limiting**
   - Implement proper rate limiting
   - Monitor for abuse patterns
   - Use IP-based restrictions

3. **Web Scraping Ethics**
   - Respect robots.txt
   - Use reasonable delays
   - Monitor for blocking

## Future Enhancements

1. **Additional Data Sources**
   - NSE/BSE direct APIs
   - Social media sentiment
   - Regulatory RSS feeds

2. **Advanced Caching**
   - Distributed caching
   - Cache warming strategies
   - Intelligent cache invalidation

3. **Machine Learning Integration**
   - Predictive caching
   - Anomaly detection
   - Automated fallback decisions

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review service health endpoints
3. Check logs for error details
4. Test with mock data to isolate issues