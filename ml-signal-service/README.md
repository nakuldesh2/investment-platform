# ML Signal Service

## Overview
The ML Signal Service uses machine learning models to generate trading signals and investment recommendations based on market data and technical indicators.

## What This Service Does

- **Signal Generation**
  - Analyzes historical stock price data to identify trading patterns
  - Generates buy/sell signals based on technical analysis
  - Provides confidence scores for each signal (0-100)

- **Machine Learning Models**
  - Trains predictive models on historical market data
  - Uses ensemble methods combining multiple algorithms
  - Continuously learns from new market data

- **Technical Indicator Calculation**
  - Computes Moving Averages (SMA, EMA)
  - Calculates RSI (Relative Strength Index)
  - Computes MACD (Moving Average Convergence Divergence)
  - Analyzes Bollinger Bands

- **Risk Assessment**
  - Evaluates volatility of stocks
  - Calculates risk-adjusted returns
  - Provides risk scores for recommended positions

- **Portfolio Recommendations**
  - Suggests optimal portfolio allocation
  - Recommends asset diversification
  - Provides rebalancing suggestions based on market conditions

- **Historical Analysis**
  - Analyzes past signal performance
  - Tracks win rate and accuracy metrics
  - Provides backtesting capabilities

## Port
- **8003**

## Endpoints

### GET `/health`
Health check endpoint
```bash
curl http://localhost:8003/health
```

### POST `/signal/{symbol}`
Generate trading signal for a stock
- **Parameters:**
  - `symbol` (path): Stock ticker symbol (e.g., AAPL, MSFT)
  - `period` (query, optional): Analysis period in days (default: 30)

**Response:**
```json
{
  "symbol": "AAPL",
  "signal": "BUY",
  "confidence": 78,
  "technical_indicators": {
    "rsi": 65.4,
    "macd": 2.15,
    "sma_50": 185.30,
    "sma_200": 180.20
  },
  "risk_score": 35,
  "generated_at": "2024-10-06T15:30:00Z"
}
```

### GET `/portfolio-recommendation`
Get portfolio recommendation
- **Parameters:**
  - `capital` (query): Investment capital amount
  - `risk_tolerance` (query): Risk tolerance level (low/medium/high)

## Environment Variables

- `ML_SIGNAL_PORT` - Port for the service (default: 8003)
- `MODEL_PATH` - Path to trained ML models
- `DATA_SOURCE_URL` - URL to fetch historical data
- `UPDATE_FREQUENCY_HOURS` - Model update frequency (default: 24)

## Dependencies

- **Python 3.9+**
- **FastAPI** - Web framework
- **scikit-learn** - Machine learning algorithms
- **pandas** - Data manipulation and analysis
- **numpy** - Numerical computing
- **tensorflow/keras** - Deep learning models (optional)

## Running Standalone

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ML_SIGNAL_PORT=8003
export MODEL_PATH=./models
export DATA_SOURCE_URL=http://localhost:8001

# Run the service
uvicorn app.main:app --host 0.0.0.0 --port 8003
```

## Model Training

```bash
# Train models on historical data
python scripts/train_models.py

# Evaluate model performance
python scripts/evaluate_models.py
```

## Service Dependencies

- Market Data Service (for fetching historical data)

## Notes

- Models are updated daily to incorporate new market data
- Signal confidence scores are based on model prediction probabilities
- Risk scores range from 0 (lowest risk) to 100 (highest risk)
- Backtest results are for educational purposes only
