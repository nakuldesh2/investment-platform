import os

import httpx
from fastapi import FastAPI, HTTPException, Query

REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "20"))
MARKET_DATA_BASE_URL = os.getenv("MARKET_DATA_BASE_URL", "http://market-data-service:8001")
NEWS_SERVICE_BASE_URL = os.getenv("NEWS_SERVICE_BASE_URL", "http://news-service:8002")
ML_SIGNAL_BASE_URL = os.getenv("ML_SIGNAL_BASE_URL", "http://ml-signal-service:8003")

app = FastAPI(title="gateway-service", version="0.1.0")


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


@app.get("/api/market/quote/{symbol}")
async def market_quote(symbol: str, mock: bool = Query(default=True)):
    return await _proxy_json(f"{MARKET_DATA_BASE_URL}/quote/{symbol}", {"mock": str(mock).lower()})


@app.get("/api/news/sentiment/{symbol}")
async def news_sentiment(symbol: str, mock: bool = Query(default=True), limit: int = Query(default=5)):
    return await _proxy_json(
        f"{NEWS_SERVICE_BASE_URL}/sentiment/{symbol}",
        {"mock": str(mock).lower(), "limit": limit},
    )


@app.get("/api/ideas/top")
async def top_ideas(symbols: str, use_mock_data: bool = Query(default=True)):
    return await _proxy_json(
        f"{ML_SIGNAL_BASE_URL}/ideas/top",
        {"symbols": symbols, "use_mock_data": str(use_mock_data).lower()},
    )


async def _proxy_json(url: str, params: dict):
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"gateway upstream error: {exc}") from exc
