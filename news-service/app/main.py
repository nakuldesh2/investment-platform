import os
from typing import Any, List, Optional

import httpx
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

MARKETAUX_API_TOKEN = os.getenv("MARKETAUX_API_TOKEN", "replace_me")
REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "20"))
MARKETAUX_URL = "https://api.marketaux.com/v1/news/all"

app = FastAPI(title="news-service", version="0.1.0")


class NewsArticle(BaseModel):
    uuid: Optional[str] = None
    title: str
    published_at: Optional[str] = None
    source: Optional[str] = None
    sentiment_score: Optional[float] = None
    url: Optional[str] = None


class SentimentResponse(BaseModel):
    symbol: str
    sentiment_score: float
    article_count: int
    source: str
    articles: List[NewsArticle]


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "news-service"}


@app.get("/sentiment/{symbol}", response_model=SentimentResponse)
async def get_sentiment(symbol: str, limit: int = Query(default=5, ge=1, le=20), mock: bool = Query(default=False)) -> SentimentResponse:
    normalized_symbol = symbol.upper()

    if mock:
        articles = [
            NewsArticle(
                uuid="mock-1",
                title=f"{normalized_symbol} gains on strong guidance",
                published_at="2026-04-15T12:00:00Z",
                source="mock-feed",
                sentiment_score=0.62,
                url="https://example.com/mock-1",
            ),
            NewsArticle(
                uuid="mock-2",
                title=f"Analysts remain constructive on {normalized_symbol}",
                published_at="2026-04-15T10:30:00Z",
                source="mock-feed",
                sentiment_score=0.41,
                url="https://example.com/mock-2",
            ),
        ]
        avg_sentiment = sum(a.sentiment_score or 0 for a in articles) / len(articles)
        return SentimentResponse(
            symbol=normalized_symbol,
            sentiment_score=round(avg_sentiment, 4),
            article_count=len(articles),
            source="mock",
            articles=articles,
        )

    params = {
        "api_token": MARKETAUX_API_TOKEN,
        "symbols": normalized_symbol,
        "language": "en",
        "limit": limit,
        "filter_entities": "true",
    }

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.get(MARKETAUX_URL, params=params)
            response.raise_for_status()
            payload = response.json()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"news provider error: {exc}") from exc

    data: List[dict[str, Any]] = payload.get("data", [])
    if not data:
        return SentimentResponse(
            symbol=normalized_symbol,
            sentiment_score=0.0,
            article_count=0,
            source="marketaux",
            articles=[],
        )

    articles: List[NewsArticle] = []
    scores: List[float] = []

    for article in data:
        entities = article.get("entities") or []
        symbol_scores = [entity.get("sentiment_score") for entity in entities if entity.get("symbol") == normalized_symbol]
        symbol_scores = [score for score in symbol_scores if isinstance(score, (int, float))]
        article_sentiment = sum(symbol_scores) / len(symbol_scores) if symbol_scores else None
        if article_sentiment is not None:
            scores.append(article_sentiment)

        articles.append(
            NewsArticle(
                uuid=article.get("uuid"),
                title=article.get("title", "Untitled article"),
                published_at=article.get("published_at"),
                source=(article.get("source") or {}).get("name") if isinstance(article.get("source"), dict) else article.get("source"),
                sentiment_score=article_sentiment,
                url=article.get("url"),
            )
        )

    avg_sentiment = sum(scores) / len(scores) if scores else 0.0

    return SentimentResponse(
        symbol=normalized_symbol,
        sentiment_score=round(avg_sentiment, 4),
        article_count=len(articles),
        source="marketaux",
        articles=articles,
    )
