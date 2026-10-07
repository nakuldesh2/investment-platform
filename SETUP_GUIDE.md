# Investment Platform - Setup Guide

Welcome to the Investment Platform! This guide will walk you through the setup process step by step.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Software Installation](#software-installation)
3. [API Keys & Accounts](#api-keys--accounts)
4. [Environment Setup](#environment-setup)
5. [Running the Services](#running-the-services)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you begin, ensure you have the following:
- A computer running macOS, Linux, or Windows
- Administrator access to install software
- Internet connection for downloading dependencies and API keys
- Approximately 2-3 GB of free disk space

---

## Software Installation

### Step 1: Install Python 3.9 or Higher

**macOS:**
```bash
# Using Homebrew
brew install python@3.9
python3 --version  # Verify installation
```
[Download Python](https://www.python.org/downloads/) if Homebrew is not installed.

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install python3.9 python3.9-venv python3-pip
python3.9 --version  # Verify installation
```

**Windows:**
1. Download from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. **Important:** Check "Add Python to PATH" during installation
4. Open PowerShell and verify: `python --version`

---

### Step 2: Install Git

**macOS:**
```bash
brew install git
git --version  # Verify installation
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install git
git --version  # Verify installation
```

**Windows:**
1. Download from [git-scm.com](https://git-scm.com/download/win)
2. Run the installer with default settings
3. Open PowerShell and verify: `git --version`

---

### Step 3: Install Docker & Docker Compose

We use Docker to run services in containers. Install Docker Desktop for your OS:

- **macOS:** [Download Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/)
- **Linux:** [Install Docker on Linux](https://docs.docker.com/engine/install/)
- **Windows:** [Download Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)

After installation, verify:
```bash
docker --version
docker-compose --version
```

---

### Step 4: Clone the Repository

```bash
# Navigate to your desired directory
cd ~/Documents  # Or any directory of your choice

# Clone the repository
git clone <repository-url>
cd investment-platform

# Verify the structure
ls -la
```

You should see directories for each service:
- `gateway-service/`
- `market-data-service/`
- `ml-signal-service/`
- `news-service/`

---

## API Keys & Accounts

You'll need API keys from external services. These are FREE tier options for getting started.

### Step 1: Alpha Vantage API Key (Market Data)

1. Visit [https://www.alphavantage.co/](https://www.alphavantage.co/)
2. Click "GET FREE API KEY" button
3. Enter your email address
4. Check your email for the API key
5. Copy the API key and save it (you'll need it in the next section)

**Free tier includes:**
- 5 API calls per minute
- 500 requests per day
- Real-time and historical stock data

---

### Step 2: NewsAPI Key (News Service)

1. Visit [https://newsapi.org/](https://newsapi.org/)
2. Click "Get API Key" button
3. Choose the "Developer" plan (free)
4. Enter your email and password
5. Copy your API key and save it

**Free tier includes:**
- 100 requests per day
- 1 month of historical news
- Access to 30,000+ news sources

---

### Step 3: Finnhub API Key (Company Data)

1. Visit [https://finnhub.io/](https://finnhub.io/)
2. Click "Get Free API Key" button
3. Enter your details and sign up
4. Copy your API key and save it

**Free tier includes:**
- 60 API calls per minute
- Real-time quotes and company information
- Economic calendars

---

## Environment Setup

### Step 1: Create Environment Variables File

Navigate to the project root and create a `.env` file:

```bash
cd investment-platform
cp .env.example .env
```

### Step 2: Edit `.env` File

Open `.env` with your text editor and fill in your API keys:

```bash
# Gateway Service
GATEWAY_PORT=8000

# Market Data Service
MARKET_DATA_SERVICE_URL=http://market-data-service:8001
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
REQUEST_TIMEOUT_SECONDS=20

# News Service
NEWS_SERVICE_URL=http://news-service:8002
NEWS_API_KEY=your_newsapi_key_here
FINNHUB_API_KEY=your_finnhub_key_here
CACHE_DURATION_MINUTES=30

# ML Signal Service
ML_SIGNAL_SERVICE_URL=http://ml-signal-service:8003
ML_SIGNAL_PORT=8003
MODEL_PATH=./models
UPDATE_FREQUENCY_HOURS=24
```

---

### Step 3: Install Python Dependencies

```bash
# Create a virtual environment (optional but recommended)
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Install dependencies for all services
pip install -r requirements.txt
```

---

## Running the Services

You have two options: run with Docker Compose or run services individually.

### Option 1: Run All Services with Docker Compose (Recommended)

```bash
cd investment-platform

# Build images (first time only)
docker-compose build

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f  # All services
docker-compose logs -f market-data-service  # Specific service
```

### Option 2: Run Services Individually

**Terminal 1 - Market Data Service:**
```bash
cd market-data-service
export ALPHA_VANTAGE_API_KEY=your_key_here
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

**Terminal 2 - News Service:**
```bash
cd news-service
export NEWS_API_KEY=your_key_here
export FINNHUB_API_KEY=your_key_here
uvicorn app.main:app --host 0.0.0.0 --port 8002
```

**Terminal 3 - ML Signal Service:**
```bash
cd ml-signal-service
uvicorn app.main:app --host 0.0.0.0 --port 8003
```

**Terminal 4 - Gateway Service:**
```bash
cd gateway-service
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## Verification

Once all services are running, verify they're working:

### Check Service Health

```bash
# Check Gateway Service
curl http://localhost:8000/health

# Check Market Data Service
curl http://localhost:8001/health

# Check News Service
curl http://localhost:8002/health

# Check ML Signal Service
curl http://localhost:8003/health
```

All should return HTTP 200 status.

### Test Market Data Service

```bash
# Test with mock data (no API key needed)
curl http://localhost:8001/quote/AAPL?mock=true

# Test with real data (requires API key)
curl http://localhost:8001/quote/AAPL
```

### Access the Gateway

```bash
# Through gateway
curl http://localhost:8000/market-data/quote/AAPL
```

---

## Troubleshooting

### Issue: "Python command not found"
- **Solution:** Reinstall Python and ensure "Add Python to PATH" is checked

### Issue: API key returns 401 Unauthorized
- **Solution:** 
  - Verify API key is correct in `.env` file
  - Check if free tier limits are exceeded
  - Wait a few minutes and try again

### Issue: "Port already in use"
- **Solution:** 
  ```bash
  # macOS/Linux - Find process using port 8000
  lsof -i :8000
  kill -9 <PID>
  
  # Windows PowerShell
  Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process
  ```

### Issue: Docker services not connecting
- **Solution:** 
  ```bash
  # Restart Docker Compose
  docker-compose down
  docker-compose up -d
  
  # Check network
  docker network ls
  docker network inspect investment-platform_default
  ```

### Issue: Slow API responses
- **Solution:**
  - Check your internet connection
  - Alpha Vantage free tier is rate-limited (5 calls/min)
  - Wait between requests or use mock data for testing

---

## Next Steps

1. **Explore the Services:** Check individual service READMEs in their directories
2. **Read API Documentation:** Visit each service's GitHub or API documentation
3. **Start Building:** Integrate services into your application
4. **Set Up Monitoring:** Configure logging and monitoring for production use

---

## Getting Help

- **Service-specific issues:** Check the README in each service directory
- **API Documentation:**
  - [Alpha Vantage Docs](https://www.alphavantage.co/documentation/)
  - [NewsAPI Docs](https://newsapi.org/docs)
  - [Finnhub Docs](https://finnhub.io/docs/api/)
- **Docker Help:** [Docker Documentation](https://docs.docker.com/)

---

Happy investing! 🚀
