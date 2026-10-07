# Market Data Service

## Overview
The Market Data Service provides real-time stock quote information by fetching data from the Alpha Vantage API.

## What This Service Does

- **Fetches Real-Time Stock Quotes**
  - Retrieves current stock price, previous close, change percentage, and trading volume
  - Uses Alpha Vantage API as the primary data source
  - Falls back to mock data when API is unavailable or rate-limited

- **Data Normalization**
  - Converts all symbols to uppercase (e.g., `aapl` → `AAPL`)
  - Parses and formats price, volume, and percentage changes
  - Handles missing or incomplete data gracefully

- **Mock Mode Support**
  - Provides consistent test data without API calls
  - Useful for development and testing scenarios
  - Returns hardcoded example stock data (AAPL: $187.42 with 1.80% change)

- **Error Handling**
  - Returns HTTP 502 if the market data provider is unreachable
  - Returns HTTP 429 if API rate limit is exceeded
  - Returns HTTP 502 if price data is malformed or missing

## Port
- **8001**

## Endpoints

### GET `/health`
Health check endpoint
```
curl http://localhost:8001/health
```

### GET `/quote/{symbol}`
Fetch stock quote for a symbol
- **Parameters:**
  - `symbol` (path): Stock ticker symbol (e.g., AAPL, MSFT)
  - `mock` (query, optional): Boolean flag to use mock data (default: false)

**Example:**
```bash
# Real data (requires API key)
curl http://localhost:8001/quote/AAPL

# Mock data (works without API key)
curl http://localhost:8001/quote/AAPL?mock=true
```

**Response:**
```json
{
  "symbol": "AAPL",
  "price": 187.42,
  "previous_close": 184.10,
  "change_percent": 1.80,
  "volume": 52341000,
  "source": "alpha_vantage"
}
```

## Environment Variables

- `ALPHA_VANTAGE_API_KEY` - Your Alpha Vantage API key (default: "demo")
- `REQUEST_TIMEOUT_SECONDS` - HTTP request timeout in seconds (default: 20)

## Dependencies

- **Python 3.9+**
- **FastAPI** - Web framework
- **httpx** - Async HTTP client
- **pydantic** - Data validation

## Running Standalone

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ALPHA_VANTAGE_API_KEY=your_key_here
export REQUEST_TIMEOUT_SECONDS=20

# Run the service
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

## Data Source

- **Primary**: Alpha Vantage API (https://www.alphavantage.co/)
- **Fallback**: Mock data for testing and development

## Notes

- The `demo` API key has limited rate limits
- Get a free API key from https://www.alphavantage.co/
- Quotes are real-time when using a valid API key
