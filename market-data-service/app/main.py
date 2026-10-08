import os
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException, Query, Header
from pydantic import BaseModel

from app.rate_limiter import alpha_vantage_limiter

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")
REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "20"))
ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query"

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
    return {"status": "ok", "service": "market-data-service"}


@app.get("/quote/{symbol}", response_model=QuoteResponse)
async def get_quote(
    symbol: str,
    mock: bool = Query(default=False),
    x_alpha_vantage_key: Optional[str] = Header(None)
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
