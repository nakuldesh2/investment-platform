import os
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException, Query, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import GatewaySettings, get_settings
from app.db import get_db, engine, Base
from app.logging_config import setup_logging, get_logger
from app.middleware.error_handler import setup_error_handling
from app.middleware.auth import setup_auth_middleware
from app.routes.auth import router as auth_router
from app.exceptions import UnauthorizedError

logger = get_logger(__name__)

REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "20"))
MARKET_DATA_BASE_URL = os.getenv("MARKET_DATA_BASE_URL", "http://market-data-service:8001")
NEWS_SERVICE_BASE_URL = os.getenv("NEWS_SERVICE_BASE_URL", "http://news-service:8002")
ML_SIGNAL_BASE_URL = os.getenv("ML_SIGNAL_BASE_URL", "http://ml-signal-service:8003")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Gateway service starting up")
    import app.models  # noqa: F401  registers tables on Base.metadata
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    logger.info("Gateway service shutting down")
    await engine.dispose()


app = FastAPI(title="gateway-service", version="0.1.0", lifespan=lifespan)

# Setup logging
setup_logging()

# Setup middleware (error handling and auth)
setup_error_handling(app)
setup_auth_middleware(app)

# Added last so it is outermost and answers preflight OPTIONS before auth runs
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        o.strip().strip("'\"").rstrip("/")
        for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
        if o.strip().strip("'\"")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register auth routes
app.include_router(auth_router)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "gateway-service",
        "downstreams": {
            "market_data": MARKET_DATA_BASE_URL,
            "news": NEWS_SERVICE_BASE_URL,
            "ml_signal": ML_SIGNAL_BASE_URL,
        },
    }


def get_current_user_id(request: Request) -> int:
    """Extract user_id from request state (set by auth middleware)"""
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise UnauthorizedError("Not authenticated")
    return user_id


async def _user_api_keys(request: Request, db: AsyncSession) -> dict:
    from app.models import User
    user = await db.get(User, get_current_user_id(request))
    return (user.api_keys or {}) if user else {}


@app.get("/api/market/quote/{symbol}")
async def market_quote(
    symbol: str,
    request: Request,
    mock: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
):
    keys = await _user_api_keys(request, db)
    headers = {"X-Alpha-Vantage-Key": keys["alpha_vantage"]} if keys.get("alpha_vantage") else {}
    return await _proxy_json(f"{MARKET_DATA_BASE_URL}/quote/{symbol}", {"mock": str(mock).lower()}, headers)


@app.get("/api/news/sentiment/{symbol}")
async def news_sentiment(
    symbol: str,
    request: Request,
    mock: bool = Query(default=False),
    limit: int = Query(default=5),
    db: AsyncSession = Depends(get_db),
):
    keys = await _user_api_keys(request, db)
    headers = {"X-Marketaux-Token": keys["marketaux"]} if keys.get("marketaux") else {}
    return await _proxy_json(
        f"{NEWS_SERVICE_BASE_URL}/sentiment/{symbol}",
        {"mock": str(mock).lower(), "limit": limit},
        headers,
    )


@app.get("/api/ideas/top")
async def top_ideas(symbols: str, use_mock_data: bool = Query(default=False)):
    return await _proxy_json(
        f"{ML_SIGNAL_BASE_URL}/ideas/top",
        {"symbols": symbols, "use_mock_data": str(use_mock_data).lower()},
    )


async def _proxy_json(url: str, params: dict, headers: dict = None):
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.get(url, params=params, headers=headers or {})
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Upstream service unreachable: {exc}") from exc
    if response.status_code >= 400:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        status = response.status_code if response.status_code in (400, 404, 429) else 502
        raise HTTPException(status_code=status, detail=detail)
    return response.json()
