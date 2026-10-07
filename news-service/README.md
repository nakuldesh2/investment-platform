# News Service

## Overview
The News Service aggregates financial news and company information from multiple sources to provide market insights and sentiment analysis for investment decision-making.

## What This Service Does

- **News Aggregation**
  - Fetches news articles from financial news APIs
  - Aggregates news from multiple sources (Reuters, Bloomberg, Yahoo Finance)
  - Filters news by relevance to specific stocks and companies
  - Provides real-time news updates

- **Sentiment Analysis**
  - Analyzes sentiment of news articles (positive, negative, neutral)
  - Calculates sentiment scores for stocks based on recent news
  - Tracks sentiment trends over time
  - Provides weighted sentiment based on source credibility

- **Company Information**
  - Retrieves company profiles and descriptions
  - Provides company financials and key metrics
  - Displays company leadership information
  - Tracks company announcements and press releases

- **Event Tracking**
  - Monitors earnings announcements and dates
  - Tracks dividend payments and stock splits
  - Identifies merger and acquisition news
  - Alerts to regulatory filings and SEC announcements

- **Trending Topics**
  - Identifies trending stocks and sectors
  - Provides hot stock picks and market movers
  - Tracks most-mentioned companies in financial news
  - Highlights emerging investment opportunities

- **News Feed**
  - Provides personalized news feeds based on portfolio holdings
  - Allows filtering by news category, source, and date range
  - Supports search across news archive

## Port
- **8002**

## Endpoints

### GET `/health`
Health check endpoint
```bash
curl http://localhost:8002/health
```

### GET `/news/{symbol}`
Fetch latest news for a stock
- **Parameters:**
  - `symbol` (path): Stock ticker symbol (e.g., AAPL, MSFT)
  - `limit` (query, optional): Number of articles to return (default: 10)
  - `days` (query, optional): Days to look back (default: 7)

**Response:**
```json
{
  "symbol": "AAPL",
  "articles": [
    {
      "title": "Apple Releases New iPhone Model",
      "source": "Reuters",
      "published_at": "2024-10-06T10:30:00Z",
      "sentiment": "positive",
      "sentiment_score": 0.85,
      "url": "https://...",
      "summary": "Apple unveiled its latest iPhone..."
    }
  ]
}
```

### GET `/sentiment/{symbol}`
Get sentiment analysis for a stock
- **Parameters:**
  - `symbol` (path): Stock ticker symbol

**Response:**
```json
{
  "symbol": "AAPL",
  "overall_sentiment": "positive",
  "sentiment_score": 0.72,
  "article_count": 45,
  "sentiment_breakdown": {
    "positive": 32,
    "neutral": 10,
    "negative": 3
  }
}
```

### GET `/trending`
Get trending stocks and topics
- **Parameters:**
  - `limit` (query, optional): Number of results (default: 10)

### GET `/company/{symbol}`
Get company information
- **Parameters:**
  - `symbol` (path): Stock ticker symbol

## Environment Variables

- `NEWS_SERVICE_PORT` - Port for the service (default: 8002)
- `NEWS_API_KEY` - API key for news data provider
- `FINNHUB_API_KEY` - Finnhub API key for company data
- `CACHE_DURATION_MINUTES` - Cache duration for news articles (default: 30)

## Dependencies

- **Python 3.9+**
- **FastAPI** - Web framework
- **httpx** - Async HTTP client
- **feedparser** - RSS feed parsing
- **textblob/transformers** - Sentiment analysis

## Running Standalone

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export NEWS_SERVICE_PORT=8002
export NEWS_API_KEY=your_api_key
export FINNHUB_API_KEY=your_finnhub_key

# Run the service
uvicorn app.main:app --host 0.0.0.0 --port 8002
```

## External APIs

- **NewsAPI** (https://newsapi.org) - Financial news articles
- **Finnhub** (https://finnhub.io) - Company data and fundamentals
- **Alpha Vantage** (https://www.alphavantage.co) - News and event data

## Notes

- News articles are cached to reduce API calls
- Sentiment analysis is performed using pre-trained models
- Source credibility scores affect sentiment weighting
- Historical news is retained for backtesting purposes
