# Gateway Service

## Overview
The Gateway Service acts as the central API gateway for the investment platform, routing requests to appropriate microservices and providing a unified interface for clients.

## What This Service Does

- **Request Routing**
  - Routes incoming requests to the appropriate microservices (Market Data, News, ML Signal services)
  - Handles URL path mapping and service discovery
  - Provides a single entry point for all client requests

- **Request/Response Handling**
  - Validates incoming requests before forwarding to services
  - Transforms and aggregates responses from multiple services
  - Standardizes response formats across the platform

- **Authentication & Authorization**
  - Validates API keys and authentication tokens
  - Enforces role-based access control (RBAC)
  - Protects sensitive endpoints with authentication middleware

- **Rate Limiting**
  - Implements rate limiting to prevent abuse
  - Tracks and limits requests per user/IP address
  - Returns HTTP 429 when rate limits are exceeded

- **Load Balancing**
  - Distributes requests across multiple service instances (when applicable)
  - Handles service failover and retry logic
  - Maintains service health checks

- **Logging & Monitoring**
  - Logs all incoming requests and outgoing responses
  - Tracks API metrics and performance
  - Provides debug information for troubleshooting

## Port
- **8000**

## Key Endpoints
- `/health` - Health check endpoint
- `/market-data/*` - Routes to Market Data Service
- `/news/*` - Routes to News Service
- `/signals/*` - Routes to ML Signal Service

## Environment Variables

- `GATEWAY_PORT` - Port for the gateway service (default: 8000)
- `MARKET_DATA_SERVICE_URL` - URL to market data service (default: http://localhost:8001)
- `NEWS_SERVICE_URL` - URL to news service (default: http://localhost:8002)
- `ML_SIGNAL_SERVICE_URL` - URL to ML signal service (default: http://localhost:8003)
- `API_KEY_SECRET` - Secret key for API authentication

## Dependencies

- **Python 3.9+**
- **FastAPI** - Web framework
- **httpx** - Async HTTP client for service-to-service communication
- **pydantic** - Data validation

## Running Standalone

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GATEWAY_PORT=8000
export MARKET_DATA_SERVICE_URL=http://localhost:8001
export NEWS_SERVICE_URL=http://localhost:8002
export ML_SIGNAL_SERVICE_URL=http://localhost:8003

# Run the service
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Service Dependencies

- Market Data Service (port 8001)
- News Service (port 8002)
- ML Signal Service (port 8003)

## Notes

- This service must be started after all downstream microservices are running
- Health checks verify connectivity to all dependent services
- Rate limiting configuration can be adjusted via environment variables
