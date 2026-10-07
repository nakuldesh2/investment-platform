import os
from typing import List, Optional

import httpx
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "20"))
MARKET_DATA_BASE_URL = os.getenv("MARKET_DATA_BASE_URL", "http://market-data-service:8001")
NEWS_SERVICE_BASE_URL = os.getenv("NEWS_SERVICE_BASE_URL", "http://news-service:8002")

app = FastAPI(title="ml-signal-service", version="0.1.0")


class InvestmentIdea(BaseModel):
    symbol: str
    score: float
    confidence: float
    current_price: float
    change_percent: Optional[float] = None
    sentiment_score: float
    article_count: int
    recommendation: str
    reason_codes: List[str]


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "ml-signal-service"}


@app.get("/ideas/top", response_model=List[InvestmentIdea])
async def get_top_ideas(
    symbols: str = Query(..., description="Comma-separated ticker list"),
    use_mock_data: bool = Query(default=True),
) -> List[InvestmentIdea]:
    symbol_list = [symbol.strip().upper() for symbol in symbols.split(",") if symbol.strip()]
    if not symbol_list:
        raise HTTPException(status_code=400, detail="At least one symbol is required")

    ideas: List[InvestmentIdea] = []

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
        for symbol in symbol_list:
            market_url = f"{MARKET_DATA_BASE_URL}/quote/{symbol}"
            news_url = f"{NEWS_SERVICE_BASE_URL}/sentiment/{symbol}"

            try:
                market_response = await client.get(market_url, params={"mock": str(use_mock_data).lower()})
                news_response = await client.get(news_url, params={"mock": str(use_mock_data).lower(), "limit": 5})
                market_response.raise_for_status()
                news_response.raise_for_status()
            except httpx.HTTPError as exc:
                raise HTTPException(status_code=502, detail=f"upstream service error for {symbol}: {exc}") from exc

            market = market_response.json()
            news = news_response.json()

            change_percent = market.get("change_percent") or 0.0
            sentiment_score = news.get("sentiment_score") or 0.0
            article_count = news.get("article_count") or 0
            volume = market.get("volume") or 0

            score = (0.55 * change_percent) + (25 * sentiment_score) + min(volume / 10_000_000, 5)
            confidence = min(0.45 + (article_count * 0.07) + (abs(sentiment_score) * 0.2), 0.95)

            reason_codes: List[str] = []
            if change_percent > 0:
                reason_codes.append("positive_price_momentum")
            else:
                reason_codes.append("weak_or_negative_price_momentum")

            if sentiment_score > 0.2:
                reason_codes.append("positive_news_sentiment")
            elif sentiment_score < -0.2:
                reason_codes.append("negative_news_sentiment")
            else:
                reason_codes.append("neutral_news_sentiment")

            if article_count >= 3:
                reason_codes.append("strong_news_coverage")
            else:
                reason_codes.append("light_news_coverage")

            recommendation = "watch"
            if score >= 12:
                recommendation = "strong_buy_candidate"
            elif score >= 6:
                recommendation = "buy_candidate"
            elif score <= -4:
                recommendation = "avoid"

            ideas.append(
                InvestmentIdea(
                    symbol=symbol,
                    score=round(score, 4),
                    confidence=round(confidence, 4),
                    current_price=market["price"],
                    change_percent=change_percent,
                    sentiment_score=sentiment_score,
                    article_count=article_count,
                    recommendation=recommendation,
                    reason_codes=reason_codes,
                )
            )

    ideas.sort(key=lambda item: item.score, reverse=True)
    return ideas
