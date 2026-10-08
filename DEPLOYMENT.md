# Deployment Guide - Investment Platform

This guide walks through deploying the Investment Platform to Railway with a public allowlist-protected URL.

## Prerequisites

- GitHub account (repository pushed to GitHub)
- Railway account (free tier available at https://railway.app)
- API keys from:
  - Alpha Vantage (https://www.alphavantage.co/)
  - NewsAPI (https://newsapi.org/)
  - Finnhub (https://finnhub.io/)
  - MarketAux (https://www.marketaux.com/)

## Architecture on Railway

```
Railway Project
├── PostgreSQL Database (managed)
├── Redis Cache (managed)
├── Gateway Service (8000) - API Gateway
├── Market Data Service (8001)
├── News Service (8002)
├── ML Signal Service (8003)
└── Frontend Service (3000) - React UI
```

## Deployment Steps

### Step 1: Create Railway Project

1. Go to https://railway.app and sign in
2. Click "New Project"
3. Select "Deploy from GitHub"
4. Authorize Railway with your GitHub account
5. Select the `nakuldesh2/investment-platform` repository
6. Click "Deploy"

### Step 2: Add PostgreSQL Database

1. In Railway Dashboard, click "Add Service"
2. Select "Database" → "PostgreSQL"
3. Railway will create a PostgreSQL instance
4. The connection string will be automatically set as `DATABASE_URL` environment variable

### Step 3: Add Redis Cache

1. Click "Add Service"
2. Select "Database" → "Redis"
3. Railway will create a Redis instance
4. The connection string will be automatically set as `REDIS_URL` environment variable

### Step 4: Configure Gateway Service

The gateway service is the API entry point.

1. In Railway Dashboard, find the "gateway-service" deployment
2. Go to "Variables"
3. Set the following environment variables:

```bash
# Core
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO

# Database (auto-set by Railway from PostgreSQL)
DATABASE_URL=postgresql+asyncpg://[user]:[password]@[host]:[port]/[database]
DATABASE_ECHO=False

# Redis (auto-set by Railway from Redis)
REDIS_URL=redis://[user]:[password]@[host]:[port]/[db]

# JWT Security (IMPORTANT: Generate secure keys!)
SECRET_KEY=<generate_32_char_random_string>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Service URLs (Railway internal networking)
MARKET_DATA_BASE_URL=http://market-data-service:8001
NEWS_SERVICE_BASE_URL=http://news-service:8002
ML_SIGNAL_BASE_URL=http://ml-signal-service:8003

# Request timeout
REQUEST_TIMEOUT_SECONDS=30

# User Allowlist (allows auto-approval without admin review)
ALLOWLIST_EMAILS=admin@example.com,yourname@example.com

# Application Settings
SERVICE_NAME=gateway-service
SERVICE_PORT=8000
```

**Generate SECRET_KEY:**
```bash
# On your machine (Python 3.6+)
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

4. Click "Deploy" to apply changes

### Step 5: Configure Market Data Service

1. Find "market-data-service" in Dashboard
2. Go to "Variables"
3. Set:

```bash
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
REQUEST_TIMEOUT_SECONDS=30
ALPHA_VANTAGE_API_KEY=<your_alpha_vantage_key>
SERVICE_NAME=market-data-service
SERVICE_PORT=8001
```

### Step 6: Configure News Service

1. Find "news-service"
2. Set:

```bash
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
REQUEST_TIMEOUT_SECONDS=30
MARKETAUX_API_TOKEN=<your_marketaux_key>
SERVICE_NAME=news-service
SERVICE_PORT=8002
```

### Step 7: Configure ML Signal Service

1. Find "ml-signal-service"
2. Set:

```bash
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
REQUEST_TIMEOUT_SECONDS=30
SERVICE_NAME=ml-signal-service
SERVICE_PORT=8003
```

### Step 8: Configure Frontend Service

1. Find "frontend-service"
2. Set:

```bash
ENVIRONMENT=production
DEBUG=False
REACT_APP_BACKEND_URL=https://<your-gateway-domain>.railway.app
```

3. The frontend service needs to be exposed as a public domain:
   - Click the "frontend-service" → "Settings"
   - Under "Domains", click "Generate Domain"
   - Copy the generated domain (e.g., `https://investment-platform-prod.up.railway.app`)

### Step 9: Update Gateway Domain

1. Click "gateway-service" → "Settings"
2. Under "Domains", click "Generate Domain"
3. Copy this domain - it's your main API endpoint

### Step 10: Initialize Database

The first deployment will automatically initialize the PostgreSQL database:

1. Railway runs the Docker container
2. The Gateway service's lifespan startup event runs `Base.metadata.create_all`
3. All tables (users, cached_quotes, cached_news, cached_signals) are created

To verify:

```bash
# Connect to PostgreSQL on Railway
psql postgresql://[user]:[password]@[host]:[port]/[database]

# List tables
\dt

# Should show: users, cached_quotes, cached_news, cached_signals
```

## Testing Deployment

### Test Registration (Non-allowlisted User)

```bash
curl -X POST https://<your-gateway-domain>/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'

# Response (status=pending)
{
  "id": 1,
  "email": "user@example.com",
  "status": "pending"
}
```

### Test Registration (Allowlisted User)

```bash
curl -X POST https://<your-gateway-domain>/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "securepassword123"
  }'

# Response (status=approved)
{
  "id": 2,
  "email": "admin@example.com",
  "status": "approved"
}
```

### Test Login (Approved User)

```bash
curl -X POST https://<your-gateway-domain>/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{
    "email": "admin@example.com",
    "password": "securepassword123"
  }'

# Response: JWT token
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### Test API Access

```bash
# Get current user (requires valid token cookie)
curl -X GET https://<your-gateway-domain>/auth/me \
  -H "Content-Type: application/json" \
  -b cookies.txt

# Get market quote
curl -X GET 'https://<your-gateway-domain>/api/market/quote/AAPL' \
  -b cookies.txt
```

### Test Frontend Access

Open `https://<your-frontend-domain>` in browser:
1. Should see login page
2. Try registering with non-allowlisted email → see "pending approval" message
3. Try registering with allowlisted email → auto-login and API key setup
4. Configure API keys
5. Access dashboard with real market data

## Security Notes

1. **JWT Secret Key**: Generate a new secure key for production (see Step 4)
2. **HTTPS Enforced**: Railway automatically provides HTTPS on all domains
3. **httpOnly Cookies**: JWT tokens stored in httpOnly cookies (XSS protection)
4. **CORS**: Configure CORS headers if frontend is on different domain (handled by Railway routing)
5. **Environment Variables**: Never commit `.env` file with real keys (use Railway Variables panel)
6. **Password Hashing**: All passwords hashed with bcrypt before storage
7. **Database Credentials**: Railway manages PostgreSQL credentials securely

## Custom Domain

To use a custom domain (e.g., `api.yourdomain.com`):

1. In Railway, go to gateway-service → Settings → Domains
2. Click "Add Custom Domain"
3. Enter your domain
4. Update DNS CNAME record to point to Railway's provided endpoint
5. Wait for DNS propagation (typically 5-30 minutes)

Example DNS Record:
```
Name: api
Type: CNAME
Value: gateway-service.up.railway.app (provided by Railway)
```

## Environment Variables Summary

| Variable | Gateway | Market Data | News | ML Signal | Frontend |
|----------|---------|-------------|------|-----------|----------|
| ENVIRONMENT | ✓ | ✓ | ✓ | ✓ | ✓ |
| DEBUG | ✓ | ✓ | ✓ | ✓ | - |
| LOG_LEVEL | ✓ | ✓ | ✓ | ✓ | - |
| SECRET_KEY | ✓ | - | - | - | - |
| JWT_ALGORITHM | ✓ | - | - | - | - |
| JWT_EXPIRATION_HOURS | ✓ | - | - | - | - |
| ALLOWLIST_EMAILS | ✓ | - | - | - | - |
| DATABASE_URL | ✓ | - | - | - | - |
| REDIS_URL | ✓ | - | - | - | - |
| ALPHA_VANTAGE_API_KEY | - | ✓ | - | - | - |
| MARKETAUX_API_TOKEN | - | - | ✓ | - | - |
| REACT_APP_BACKEND_URL | - | - | - | - | ✓ |
| SERVICE_PORT | ✓ | ✓ | ✓ | ✓ | - |
| SERVICE_NAME | ✓ | ✓ | ✓ | ✓ | - |
| MARKET_DATA_BASE_URL | ✓ | - | - | - | - |
| NEWS_SERVICE_BASE_URL | ✓ | - | - | - | - |
| ML_SIGNAL_BASE_URL | ✓ | - | - | - | - |

## Troubleshooting

### Services won't start
- Check Railway logs: Dashboard → Service → Logs
- Verify environment variables are set correctly
- Ensure DATABASE_URL and REDIS_URL include credentials

### Database connection errors
- Wait 2-3 minutes after adding PostgreSQL service
- Verify DATABASE_URL is correct format
- Check PostgreSQL service is healthy in Railway

### Frontend can't reach API
- Verify REACT_APP_BACKEND_URL is set correctly
- Check gateway-service has public domain assigned
- Verify CORS headers (handled by Railway proxy)

### Users can't register
- Check ALLOWLIST_EMAILS configuration
- Verify database is initialized (check PostgreSQL logs)
- Look for database constraint errors in gateway-service logs

## Rollback

To rollback to a previous deployment:

1. In Railway, go to Deployments
2. Find the previous successful deployment
3. Click "Redeploy"

All services will revert to the previous version.

## Next Steps

1. Add CI/CD pipeline (GitHub Actions) for automated deployments
2. Set up monitoring and alerts
3. Add backup strategy for PostgreSQL
4. Implement audit logging
5. Set up admin dashboard for user management
6. Add rate limiting at gateway level
