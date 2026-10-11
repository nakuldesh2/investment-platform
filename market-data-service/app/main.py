import os
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException, Query, Header
from pydantic import BaseModel

from app.rate_limiter import alpha_vantage_limiter

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")
REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "20"))
ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query"

ALPACA_API_KEY = os.getenv("ALPACA_API_KEY", "")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY", "")
ALPACA_DATA_URL = os.getenv("ALPACA_DATA_URL", "https://data.alpaca.markets")
ALPACA_FEED = os.getenv("ALPACA_FEED", "iex")  # free plan only includes the IEX feed

app = FastAPI(title="market-data-service", version="0.1.0")


class QuoteResponse(BaseModel):
    symbol: str
    price: float
    previous_close: Optional[float] = None
    change_percent: Optional[float] = None
    volume: Optional[int] = None
    source: str


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "market-data-service",
        "provider": "alpaca" if ALPACA_API_KEY and ALPACA_SECRET_KEY else "alpha_vantage",
        "feed": ALPACA_FEED,
    }


class AlpacaUnavailable(Exception):
    """Alpaca could not serve the quote; caller may fall back to Alpha Vantage."""


async def _alpaca_quote(symbol: str, key_id: str, secret: str) -> QuoteResponse:
    url = f"{ALPACA_DATA_URL}/v2/stocks/{symbol}/snapshot"
    headers = {"APCA-API-KEY-ID": key_id, "APCA-API-SECRET-KEY": secret}
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.get(url, params={"feed": ALPACA_FEED}, headers=headers)
    except httpx.HTTPError as exc:
        raise AlpacaUnavailable(f"alpaca unreachable: {exc}") from exc

    if response.status_code in (404, 422):
        raise HTTPException(status_code=404, detail=f"Unknown symbol: {symbol}")
    if response.status_code >= 400:
        raise AlpacaUnavailable(f"alpaca returned {response.status_code}: {response.text[:200]}")

    snap = response.json()
    latest_trade = snap.get("latestTrade") or {}
    daily_bar = snap.get("dailyBar") or {}
    prev_bar = snap.get("prevDailyBar") or {}

    price = latest_trade.get("p") or daily_bar.get("c")
    if price is None:
        raise AlpacaUnavailable("alpaca snapshot missing price")

    previous_close = prev_bar.get("c")
    change_percent = (
        round((price - previous_close) / previous_close * 100, 2) if previous_close else None
    )
    volume = daily_bar.get("v")

    return QuoteResponse(
        symbol=symbol,
        price=float(price),
        previous_close=float(previous_close) if previous_close is not None else None,
        change_percent=change_percent,
        volume=int(volume) if volume is not None else None,
        source=f"alpaca_{ALPACA_FEED}",
    )


@app.get("/quote/{symbol}", response_model=QuoteResponse)
async def get_quote(
    symbol: str,
    mock: bool = Query(default=False),
    x_alpha_vantage_key: Optional[str] = Header(None),
    x_alpaca_key_id: Optional[str] = Header(None),
    x_alpaca_secret: Optional[str] = Header(None),
) -> QuoteResponse:
    normalized_symbol = symbol.upper()

    if mock:
        return QuoteResponse(
            symbol=normalized_symbol,
            price=187.42,
            previous_close=184.10,
            change_percent=1.80,
            volume=52341000,
            source="mock",
        )

    # Prefer Alpaca (user's keys from the gateway, else env keys); fall back to Alpha Vantage
    alpaca_key_id, alpaca_secret = (
        (x_alpaca_key_id, x_alpaca_secret)
        if x_alpaca_key_id and x_alpaca_secret
        else (ALPACA_API_KEY, ALPACA_SECRET_KEY)
    )
    alpaca_error = None
    if alpaca_key_id and alpaca_secret:
        try:
            return await _alpaca_quote(normalized_symbol, alpaca_key_id, alpaca_secret)
        except AlpacaUnavailable as exc:
            alpaca_error = str(exc)

    # Use API key from header or fallback to environment variable
    api_key = x_alpha_vantage_key or ALPHA_VANTAGE_API_KEY

    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": normalized_symbol,
        "apikey": api_key,
    }

    # Respect rate limits (5 calls/min for Alpha Vantage free tier)
    await alpha_vantage_limiter.wait_if_needed()

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.get(ALPHA_VANTAGE_URL, params=params)
            response.raise_for_status()
            payload = response.json()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"market provider error: {exc}") from exc

    quote = payload.get("Global Quote", {})
    if not quote:
        note = payload.get("Note") or payload.get("Information") or "No quote returned"
        if alpaca_error:
            note = f"{alpaca_error}; Alpha Vantage fallback: {note}"
        raise HTTPException(status_code=429, detail=note)

    def _to_float(value: Optional[str]) -> Optional[float]:
        if value in (None, ""):
            return None
        return float(value)

    def _to_int(value: Optional[str]) -> Optional[int]:
        if value in (None, ""):
            return None
        return int(float(value))

    price = _to_float(quote.get("05. price"))
    previous_close = _to_float(quote.get("08. previous close"))
    change_percent_raw = quote.get("10. change percent")
    change_percent = float(change_percent_raw.replace("%", "")) if change_percent_raw else None

    if price is None:
        raise HTTPException(status_code=502, detail="quote payload missing price")

    return QuoteResponse(
        symbol=normalized_symbol,
        price=price,
        previous_close=previous_close,
        change_percent=change_percent,
        volume=_to_int(quote.get("06. volume")),
        source="alpha_vantage",
    )
