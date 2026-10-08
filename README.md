# Investment Research Platform

An enterprise-grade microservices platform for AI-assisted investment analysis with real market data APIs, user authentication, and allowlist-based access control.

## 🚀 Quick Links

### For Development
- **Setup:** See [CLAUDE.md](CLAUDE.md) for development guidelines
- **Local Development:** Follow "Run Locally" section below
- **Docker Compose:** Uses PostgreSQL, Redis, and 5 microservices

### For Deployment (Railway)
- **⭐ Start Here:** [RAILWAY_QUICKSTART.md](RAILWAY_QUICKSTART.md) (5-minute setup)
- **Full Guide:** [DEPLOYMENT.md](DEPLOYMENT.md) (comprehensive guide)
- **Setup Card:** [RAILWAY_SETUP_CARD.txt](RAILWAY_SETUP_CARD.txt) (reference card)
- **Checklist:** [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) (verification steps)

## 📋 System Architecture

### Microservices
| Service | Port | Purpose |
|---------|------|---------|
| **gateway-service** | 8000 | API Gateway - authentication & routing |
| **market-data-service** | 8001 | Real-time stock quotes (Alpha Vantage) |
| **news-service** | 8002 | Financial news & sentiment (MarketAux) |
| **ml-signal-service** | 8003 | Investment signal generation |
| **frontend-service** | 3000 | React UI dashboard |

### Data Layer
- **PostgreSQL:** User accounts, API keys, cached data
- **Redis:** Session cache, rate limiting

## 🔐 Security Features

✅ **User Authentication**
- JWT tokens in httpOnly cookies (XSS-safe)
- Password hashing with bcrypt
- 24-hour token expiration

✅ **Access Control**
- Email allowlist for auto-approval
- Pending user status tracking
- Admin approval workflow for non-allowlisted users

✅ **API Key Management**
- Secure storage in PostgreSQL
- Per-user API key configuration
- Server-side storage (not localStorage)

✅ **Deployment Security**
- HTTPS/TLS automatic on Railway
- Environment variables for secrets
- No hardcoded API keys

## 🏠 Local Development

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for direct service running)
- Node 16+ (for frontend)
- API keys from:
  - [Alpha Vantage](https://www.alphavantage.co/) (free, 5 calls/min)
  - [MarketAux](https://www.marketaux.com/) (optional)
  - [NewsAPI](https://newsapi.org/) (optional)

### Quick Start
```bash
# Clone and setup
git clone https://github.com/nakuldesh2/investment-platform.git
cd investment-platform
cp .env.example .env

# Edit .env and add your API keys
# (or use mock mode without keys)

# Build and run all services
docker compose up --build

# Services start automatically on:
# - Gateway: http://localhost:8000
# - Frontend: http://localhost:3000
```

### Test Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Register user (auto-approved if in ALLOWLIST_EMAILS)
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"testpass123"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"email":"user@example.com","password":"testpass123"}'

# Get authenticated user
curl http://localhost:8000/auth/me -b cookies.txt

# Market data
curl http://localhost:8000/api/market/quote/AAPL

# News sentiment
curl http://localhost:8000/api/news/sentiment/AAPL

# Investment signals
curl http://localhost:8000/api/ideas/top?symbols=AAPL,MSFT
```

## 🧪 Testing

### Frontend Testing
1. Open http://localhost:3000
2. Register with email in ALLOWLIST_EMAILS
3. Configure API keys
4. View dashboard with real market data

### API Testing
```bash
# Run through auth flow
# Register → Login → Set API Keys → Access Dashboard
```

## 📊 Data Flow

```
User (Browser)
    ↓
Frontend Service (React UI, port 3000)
    ↓
Gateway Service (Auth, routing, port 8000)
    ├→ Market Data Service (Alpha Vantage, port 8001)
    ├→ News Service (MarketAux, port 8002)
    └→ ML Signal Service (rankings, port 8003)
    ↓
PostgreSQL Database (user accounts, API keys)
Redis Cache (sessions, rate limiting)
```

## 📁 Project Structure

```
investment-platform/
├── gateway-service/          # API Gateway & authentication
├── market-data-service/      # Stock quotes service
├── news-service/             # News & sentiment analysis
├── ml-signal-service/        # Signal generation
├── frontend-service/         # React dashboard
├── docker-compose.yml        # Multi-service orchestration
├── .env.example              # Configuration template
├── CLAUDE.md                 # Development guidelines
├── DEPLOYMENT.md             # Railway deployment guide
├── RAILWAY_QUICKSTART.md     # 5-minute setup
└── scripts/deploy-railway.sh # Deployment helper
```

## 🚀 Deployment (Railway)

### One-Click Deployment
1. Push repository to GitHub
2. Go to [railway.app](https://railway.app)
3. Create new project → Deploy from GitHub
4. Select this repository
5. Railway auto-detects and deploys all services

### Configuration
Follow [RAILWAY_QUICKSTART.md](RAILWAY_QUICKSTART.md) to:
- Set up PostgreSQL & Redis (auto-managed)
- Configure environment variables
- Assign public domains
- Test allowlist protection

### Result
Your platform is live with:
- ✅ Public URL (HTTPS automatic)
- ✅ Allowlist-protected access
- ✅ Real market data APIs
- ✅ Secure user authentication
- ✅ API key management

**Share only the frontend URL with allowlisted users!**

## 🔧 Configuration

### Environment Variables

**Core Services** (all services):
```bash
ENVIRONMENT=development|production
DEBUG=True|False
LOG_LEVEL=INFO|DEBUG
REQUEST_TIMEOUT_SECONDS=20
```

**Gateway Service** (authentication):
```bash
SECRET_KEY=<unique_32_char_key>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
ALLOWLIST_EMAILS=admin@example.com,user@example.com
```

**API Keys**:
```bash
ALPHA_VANTAGE_API_KEY=<your_key>
MARKETAUX_API_TOKEN=<your_key>
```

**Database** (Railway auto-sets):
```bash
DATABASE_URL=postgresql+asyncpg://...
REDIS_URL=redis://...
```

See [.env.example](.env.example) for complete reference.

## 📈 Features

### User Management
- ✅ Registration with email validation
- ✅ Allowlist-based auto-approval
- ✅ Pending user workflow
- ✅ Secure password hashing (bcrypt)
- ✅ JWT authentication

### Market Data
- ✅ Real-time stock quotes
- ✅ Price change tracking
- ✅ Volume metrics
- ✅ Rate limiting (5 calls/min free tier)

### News & Sentiment
- ✅ Financial news aggregation
- ✅ Sentiment scoring (-1 to +1)
- ✅ Article URL references
- ✅ Publisher information

### Investment Signals
- ✅ AI-powered rankings
- ✅ Confidence scores
- ✅ Reason codes
- ✅ Multi-factor analysis

### Security
- ✅ HTTPS/TLS encryption
- ✅ httpOnly cookie storage
- ✅ XSS protection
- ✅ CSRF tokens
- ✅ Rate limiting

## 🛠️ Development

### Running Services Individually

Each service can run standalone:

```bash
# Market Data Service
export ALPHA_VANTAGE_API_KEY=your_key
uvicorn app.main:app --reload --port 8001 --app-dir=market-data-service

# News Service
export MARKETAUX_API_TOKEN=your_key
uvicorn app.main:app --reload --port 8002 --app-dir=news-service

# ML Signal Service
uvicorn app.main:app --reload --port 8003 --app-dir=ml-signal-service

# Gateway Service
uvicorn app.main:app --reload --port 8000 --app-dir=gateway-service

# Frontend (separate terminal)
cd frontend-service && npm start
```

### Development Tools
- **Linting:** No linter configured yet (can add Ruff)
- **Type Checking:** No mypy configured yet
- **Testing:** No test suite yet (pytest recommended)
- **Pre-commit:** No hooks configured yet

See [CLAUDE.md](CLAUDE.md) for development setup.

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [CLAUDE.md](CLAUDE.md) | Development guidelines & architecture |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Full Railway deployment guide |
| [RAILWAY_QUICKSTART.md](RAILWAY_QUICKSTART.md) | 5-minute setup for Railway |
| [RAILWAY_SETUP_CARD.txt](RAILWAY_SETUP_CARD.txt) | Quick reference for deployment |
| [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) | Verification checklist |
| [.env.example](.env.example) | Configuration reference |

## 🐛 Troubleshooting

### Services won't start?
```bash
# Check Docker logs
docker compose logs -f <service-name>

# Rebuild without cache
docker compose build --no-cache
```

### Database connection errors?
```bash
# Verify PostgreSQL is healthy
docker compose ps postgres

# Wait 2-3 minutes for initialization
# Check gateway logs for initialization message
```

### Frontend can't reach API?
```bash
# Verify backend URL in .env
# Test gateway health: curl http://localhost:8000/health
# Check CORS headers are set
```

See [DEPLOYMENT.md](DEPLOYMENT.md#troubleshooting) for more solutions.

## 📝 License

Created for enterprise-grade investment analysis platform.

## 🤝 Contributing

This is an active development project. See [CLAUDE.md](CLAUDE.md) for contribution guidelines.

---

**Ready to deploy?** Start with [RAILWAY_QUICKSTART.md](RAILWAY_QUICKSTART.md) 🚀
