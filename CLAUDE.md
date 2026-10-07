# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Investment Research Platform** is a multi-service microservices architecture for AI-assisted investment analysis. It aggregates real-time market data, financial news, and ML-generated signals through a unified API gateway.

**Tech Stack:**
- **Backend:** FastAPI (Python 3.11+) with async/await patterns
- **Frontend:** React 18 with Axios for API communication
- **Orchestration:** Docker Compose for local development
- **External APIs:** Alpha Vantage (market data), NewsAPI/Finnhub (news/company data)

## Service Architecture

### Services (Microservices Pattern)

1. **Gateway Service (port 8000)** - API entry point
   - Aggregates requests across all downstream services
   - Serves `/api/*` endpoints
   - Acts as a reverse proxy with error handling
   - File: `gateway-service/app/main.py`

2. **Market Data Service (port 8001)** - Stock quotes
   - Fetches real-time quotes from Alpha Vantage API
   - Normalizes symbol format (uppercase)
   - Supports mock data for testing without API keys
   - File: `market-data-service/app/main.py`

3. **News Service (port 8002)** - Financial news & sentiment
   - Aggregates news from NewsAPI and company data from Finnhub
   - Calculates sentiment scores from article headlines
   - Returns mock data when APIs are rate-limited
   - File: `news-service/app/main.py`

4. **ML Signal Service (port 8003)** - Investment recommendations
   - Combines market data + news sentiment to generate investment ideas
   - Scores symbols based on price momentum, sentiment, and volume
   - Returns ranked list with confidence scores and reasoning
   - File: `ml-signal-service/app/main.py`

5. **Frontend Service** - React UI (port 3000 in development)
   - Dashboard for viewing quotes, news, and signals
   - Stock search interface
   - API key configuration (client-side)
   - Files: `frontend-service/src/components/*.js`

### Communication Pattern

```
Client → Gateway (8000) → Market Data (8001)
                       → News Service (8002)
                       → ML Signal Service (8003)
```

All inter-service communication uses **httpx** (async HTTP client) with shared `REQUEST_TIMEOUT_SECONDS` env var (default 20s).

## Development Setup

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for running services individually)
- Node 16+ (for frontend)
- API keys: Alpha Vantage (free at alphavantage.co), optional NewsAPI/Finnhub

### Quick Start

```bash
# 1. Clone and configure
cd investment-platform
cp .env.example .env
# Edit .env and add your API keys

# 2. Start all services with Docker
docker compose up --build

# 3. Verify services are running
curl http://localhost:8000/health
```

### Run Services Individually

Each service uses **uvicorn** (ASGI server). Install dependencies first:

```bash
# Install Python dependencies
pip install -r market-data-service/requirements.txt
pip install -r news-service/requirements.txt
pip install -r ml-signal-service/requirements.txt
pip install -r gateway-service/requirements.txt
```

Then run in separate terminals:

```bash
# Terminal 1 - Market Data
export ALPHA_VANTAGE_API_KEY=your_key
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload --app-dir=market-data-service

# Terminal 2 - News Service
export NEWS_API_KEY=your_key
export FINNHUB_API_KEY=your_key
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload --app-dir=news-service

# Terminal 3 - ML Signal Service
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload --app-dir=ml-signal-service

# Terminal 4 - Gateway
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --app-dir=gateway-service

# Terminal 5 - Frontend (separate from backend)
cd frontend-service && npm start
```

## Build and Run Commands

### Docker Compose (All Services)

```bash
# Build images (required first time or after dependency changes)
docker compose build

# Start services in foreground (useful for debugging)
docker compose up

# Start in background
docker compose up -d

# View logs
docker compose logs -f                    # All services
docker compose logs -f market-data-service  # Single service

# Stop and clean up
docker compose down

# Rebuild without cache (if dependencies are stale)
docker compose build --no-cache
```

### Backend Service Development (Python)

```bash
# Lint code (no linter configured; can add ruff or black)
# TODO: Add pre-commit hooks or CI lint step

# Run type checking
# TODO: Add mypy configuration

# Run a specific service with hot-reload
uvicorn app.main:app --reload --port <SERVICE_PORT> --app-dir=<service-name>
```

### Frontend Development (React)

```bash
cd frontend-service

# Install dependencies
npm install

# Development server (hot reload on localhost:3000)
npm start

# Build for production
npm build

# Run tests (if configured)
npm test
```

## Testing

**Current Status:** No test suite exists yet.

**Recommended approach (enterprise-style):**

```bash
# Python testing: pytest + pytest-asyncio for async endpoints
# Example command (once configured):
pytest market-data-service/tests/ -v

# Frontend testing: Jest + React Testing Library
# Example command (once configured):
npm test --prefix=frontend-service
```

Each service should have a `tests/` directory with:
- Unit tests for business logic (e.g., data parsing)
- Integration tests for endpoints (mocking downstream services)
- Mock data fixtures (already in code as `mock=true` query param)

## Key Architecture Patterns

### FastAPI Service Template

All backend services follow this pattern:

```python
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

app = FastAPI(title="service-name", version="0.1.0")

class ResponseModel(BaseModel):
    field: str
    # Pydantic auto-validates and documents fields

@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "service-name"}

@app.get("/endpoint/{param}")
async def endpoint(param: str, optional: bool = Query(default=False)):
    # Use httpx.AsyncClient for inter-service calls
    try:
        # Handle business logic
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Upstream error: {exc}")
```

**Key patterns:**
- Use **Pydantic models** for request/response validation
- Use **async/await** for all I/O operations
- Return **proper HTTP status codes** (502 for upstream errors, 429 for rate limits, 400 for client errors)
- Raise **HTTPException** rather than returning error responses
- Read config from **environment variables** with sensible defaults

### Environment Variables

All services use `os.getenv()` for configuration. Key variables:

| Variable | Purpose | Default |
|----------|---------|---------|
| `REQUEST_TIMEOUT_SECONDS` | HTTP timeout for inter-service calls | `20` |
| `ALPHA_VANTAGE_API_KEY` | Market data API key | `"demo"` |
| `NEWS_API_KEY` / `FINNHUB_API_KEY` | News/company data API keys | - |
| `MARKET_DATA_BASE_URL` | Market service URL | `http://market-data-service:8001` |
| `NEWS_SERVICE_BASE_URL` | News service URL | `http://news-service:8002` |
| `ML_SIGNAL_BASE_URL` | ML service URL | `http://ml-signal-service:8003` |

These are shared in `.env` (never commit) and `.env.example` (template for new devs).

### Error Handling Pattern

Services distinguish error types:

- **502 Bad Gateway** - Upstream service unreachable or returned error
- **429 Too Many Requests** - API rate limit exceeded (e.g., Alpha Vantage `Note` field)
- **400 Bad Request** - Invalid input (e.g., no symbols provided)
- **200 OK with mock data** - When APIs fail but mock data is available

Example from `market-data-service/app/main.py`:

```python
if not quote:
    note = payload.get("Note") or payload.get("Information")
    raise HTTPException(status_code=429, detail=note)  # Rate limit
```

### Mock Data Strategy

Services support `mock=true` query parameter for development/testing **without API keys**:

```bash
curl http://localhost:8001/quote/AAPL?mock=true  # Returns hardcoded data
curl http://localhost:8000/api/ideas/top?symbols=AAPL,MSFT&use_mock_data=true
```

This is critical for:
- Local testing without valid API keys
- CI/CD pipelines
- Rate limit recovery during development

## Frontend Architecture

**Framework:** React 18 with CSS (no CSS framework configured yet)

**Structure:**
- `src/App.js` - Main app component
- `src/components/` - Reusable components:
  - `Dashboard.js` - Main layout
  - `StockSearch.js` - Search interface
  - `SignalsSection.js` - ML signal display
  - `NewsSection.js` - News aggregation
  - `ApiKeySetup.js` - API key configuration
- `src/index.js` - Entry point
- `public/` - Static assets

**Key dependencies:**
- **axios** - HTTP client (points to gateway at `http://localhost:8000`)
- **react-router-dom** - Routing (currently minimal setup)
- **lucide-react** - Icons

**Development:** No build tooling beyond react-scripts (CRA standard).

## Common Development Tasks

### Add a New Endpoint to a Service

1. Define request/response models in `app/main.py`:
   ```python
   class MyResponse(BaseModel):
       field: str
   ```

2. Add endpoint with proper error handling:
   ```python
   @app.get("/endpoint/{id}")
   async def my_endpoint(id: str):
       try:
           # Logic here
       except httpx.HTTPError as exc:
           raise HTTPException(status_code=502, detail=str(exc))
   ```

3. Test with: `curl http://localhost:PORT/endpoint/test-id`

4. Update `.env.example` if adding new env vars

### Add a Downstream Service Call

Services call each other using **httpx**:

```python
import httpx

async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
    response = await client.get(f"{MARKET_DATA_BASE_URL}/quote/{symbol}")
    response.raise_for_status()
    data = response.json()
```

### Restart Docker Services

After code changes:

```bash
docker compose restart gateway-service
# Or rebuild if dependencies changed
docker compose up -d --build
```

### Debug a Service

View logs in real-time:

```bash
docker compose logs -f ml-signal-service
```

Or run with print statements for local testing:

```bash
uvicorn app.main:app --reload --port 8003 --app-dir=ml-signal-service
# Run requests and watch console output
```

### Configure API Keys

1. Get API keys from:
   - **Alpha Vantage:** alphavantage.co (free, 5 calls/min)
   - **NewsAPI:** newsapi.org (100 requests/day)
   - **Finnhub:** finnhub.io (60 calls/min)

2. Add to `.env`:
   ```bash
   ALPHA_VANTAGE_API_KEY=your_actual_key
   NEWS_API_KEY=your_newsapi_key
   FINNHUB_API_KEY=your_finnhub_key
   ```

3. Services will use these keys when `mock=false` or not specified.

## Next Steps / Enterprise Improvements

The codebase is intentionally simple to run locally quickly. To scale to production:

- **Database:** Add PostgreSQL for persistence (user watchlists, historical data, cached quotes)
- **Message Queue:** Add Kafka/RabbitMQ for decoupled service communication
- **Testing:** Add pytest + pytest-asyncio for backend, Jest for frontend
- **Logging:** Add structured logging (e.g., `python-json-logger`) instead of stdout
- **Monitoring:** Add Prometheus metrics and health check aggregation
- **CI/CD:** Add GitHub Actions for lint, test, build, deploy
- **Configuration:** Move to `.yaml` or `config/` layer for environment-specific overrides
- **API Versioning:** Prefix endpoints with `/v1/` for backward compatibility
- **Authentication:** Add JWT or API key validation at gateway layer
- **Rate Limiting:** Add per-client rate limits at gateway
- **Caching:** Add Redis for frequently accessed quotes/news

## File Reference

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Service orchestration (ports, volumes, env, dependencies) |
| `.env.example` | Template for environment variables |
| `.gitignore` | Standard Python + Node ignores (secrets, deps, cache) |
| `gateway-service/app/main.py` | API gateway & request routing |
| `market-data-service/app/main.py` | Stock quote fetching & normalization |
| `news-service/app/main.py` | News sentiment aggregation |
| `ml-signal-service/app/main.py` | Signal scoring & ranking |
| `frontend-service/src/App.js` | React root component |
| `*/requirements.txt` | Python package dependencies per service |
| `*/Dockerfile` | Container image definition (Python 3.11 slim base) |

---

**Last Updated:** 2026-10-06
