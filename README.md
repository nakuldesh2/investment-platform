# Investment Research Platform Prototype

This is a local multi-service prototype for an AI-assisted investment idea platform.

## Services
- `market-data-service`: pulls market snapshots from Alpha Vantage and a fallback mock path
- `news-service`: pulls finance news from Marketaux and calculates simple sentiment aggregates
- `ml-signal-service`: builds features from market + news data and ranks symbols
- `gateway-service`: aggregates all services into one entry point

## Why this version is practical
This first cut uses REST between services so you can get a running system locally very quickly. Once stable, you can add Kafka/RabbitMQ, persistence, and scheduled ingestion.

## Run locally
```bash
cp .env.example .env
# fill in your real keys if you have them

docker compose up --build
```

## Test endpoints
```bash
curl http://localhost:8000/health
curl "http://localhost:8000/api/market/quote/AAPL"
curl "http://localhost:8000/api/news/sentiment/AAPL"
curl "http://localhost:8000/api/ideas/top?symbols=AAPL,MSFT,NVDA"
```

## Main flow
1. Gateway receives a request for ideas.
2. ML service requests latest market data from market-data-service.
3. ML service requests news sentiment from news-service.
4. ML service builds features and returns a ranked list of trade ideas.

## Current scoring logic
This is a simple baseline, not a real production model:
- positive price change improves score
- positive sentiment improves score
- higher volume improves score slightly
- reason codes explain why a symbol ranked well or poorly

## Next upgrades
- add PostgreSQL and Redis
- add Kafka or RabbitMQ
- add historical candles and feature store
- replace scoring formula with a trained model
- add backtesting and paper trading
