# Deploy to Railway - Complete Guide

## Prerequisites (5 minutes)

### 1. Generate Secret Key
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```
**Copy and save the output.**

### 2. Get API Keys
- **Alpha Vantage:** https://www.alphavantage.co/ (free)
- **MarketAux:** https://www.marketaux.com/ (free)

### 3. Create Railway Account
Go to https://railway.app and sign up (free tier)

### 4. Know Your Email
This email will be auto-approved to access the platform.

---

## Deploy Services (25 minutes)

### Step 1: Create Empty Project
1. Go to https://railway.app
2. Click **"New Project"** → **"Empty Project"**

### Step 2: Add Gateway Service
1. Click **"+ New Service"** → **"GitHub Repo"**
2. Select **`nakuldesh2/investment-platform`**
3. In Settings tab, click **"Add Root Directory"**
4. Enter: `gateway-service`
5. Click **"Variables"** tab
6. Add variables:
```
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=<paste_your_secret_key>
ALLOWLIST_EMAILS=<your_email>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
SERVICE_NAME=gateway-service
SERVICE_PORT=8000
REQUEST_TIMEOUT_SECONDS=30
MARKET_DATA_BASE_URL=http://market-data-service:8001
NEWS_SERVICE_BASE_URL=http://news-service:8002
ML_SIGNAL_BASE_URL=http://ml-signal-service:8003
```

### Step 3: Add Market Data Service
1. Click **"+ New Service"** → **"GitHub Repo"**
2. Select **`nakuldesh2/investment-platform`**
3. Click **"Add Root Directory"** → Enter: `market-data-service`
4. Click **"Variables"** tab
5. Add:
```
ENVIRONMENT=production
DEBUG=False
ALPHA_VANTAGE_API_KEY=<your_api_key>
SERVICE_NAME=market-data-service
SERVICE_PORT=8001
REQUEST_TIMEOUT_SECONDS=30
```

### Step 4: Add News Service
1. Click **"+ New Service"** → **"GitHub Repo"**
2. Select **`nakuldesh2/investment-platform`**
3. Click **"Add Root Directory"** → Enter: `news-service`
4. Click **"Variables"** tab
5. Add:
```
ENVIRONMENT=production
DEBUG=False
MARKETAUX_API_TOKEN=<your_token>
SERVICE_NAME=news-service
SERVICE_PORT=8002
REQUEST_TIMEOUT_SECONDS=30
```

### Step 5: Add ML Signal Service
1. Click **"+ New Service"** → **"GitHub Repo"**
2. Select **`nakuldesh2/investment-platform`**
3. Click **"Add Root Directory"** → Enter: `ml-signal-service`
4. Click **"Variables"** tab
5. Add:
```
ENVIRONMENT=production
DEBUG=False
SERVICE_NAME=ml-signal-service
SERVICE_PORT=8003
REQUEST_TIMEOUT_SECONDS=30
```

### Step 6: Add PostgreSQL Database
1. Click **"+ New Service"** → **"Database"** → **"PostgreSQL"**
2. Railway creates it automatically with a DATABASE_URL

### Step 7: Add Redis Cache
1. Click **"+ New Service"** → **"Database"** → **"Redis"**
2. Railway creates it automatically with a REDIS_URL

### Step 8: Add Frontend Service
1. Click **"+ New Service"** → **"GitHub Repo"**
2. Select **`nakuldesh2/investment-platform`**
3. Click **"Add Root Directory"** → Enter: `frontend-service`
4. Click **"Settings"** → Scroll to **"Domains"** → **"Generate Domain"**
5. **Copy the domain** (you'll need it next)
6. Click **"Variables"** tab
7. Add:
```
REACT_APP_BACKEND_URL=https://<paste_gateway_domain>
ENVIRONMENT=production
DEBUG=False
```
(Replace `<paste_gateway_domain>` with the gateway-service domain)

### Step 9: Get Gateway Domain
1. Click on **gateway-service** in your services list
2. Click **"Settings"** → Scroll to **"Domains"**
3. Click **"Generate Domain"** (if not already done)
4. **Copy this domain** - it's your API endpoint

### Step 10: Update Frontend Domain Variable
1. Go back to **frontend-service**
2. Click **"Variables"** tab
3. Find **`REACT_APP_BACKEND_URL`**
4. Update it with the gateway domain you just copied:
```
REACT_APP_BACKEND_URL=https://<gateway-domain>
```

### Step 11: Deploy All Services
1. At the top, you should see **"Apply X changes"** button
2. Click **"Deploy"** button
3. Wait 10-15 minutes for all services to build and deploy

### Step 12: Wait for Services to Go Green
Monitor the dashboard. All services should show:
- ✅ Green status
- ✅ "Active" state

Services list:
- gateway-service ✅
- market-data-service ✅
- news-service ✅
- ml-signal-service ✅
- frontend-service ✅
- postgres ✅
- redis ✅

### Step 13: Get Frontend Public URL
1. Click on **frontend-service**
2. Click **"Settings"** → **"Domains"**
3. **Copy the public domain** - this is your app URL!

### Step 14: Test Your Platform
1. Open browser: `https://<your-frontend-domain>`
2. Click **"Create Account"**
3. Enter your email (the allowlisted one) and password
4. Should auto-login
5. Configure API keys
6. View dashboard with real market data
7. Test logout and login

---

## That's It! 🎉

Your platform is now:
- ✅ Live on public HTTPS URL
- ✅ Protected by allowlist
- ✅ Using real market data
- ✅ Cost: $0/month

**Share the frontend URL only with allowlisted users.**

---

## Troubleshooting

**Services still red after 15 minutes?**
- Click service → "Logs" → check for errors
- Common: missing DATABASE_URL or REDIS_URL (should auto-populate)

**Can't reach frontend?**
- Check domain was generated
- Refresh browser
- Wait 2-3 more minutes

**Login fails?**
- Verify email is in ALLOWLIST_EMAILS
- Try incognito window
- Check gateway-service logs for errors

**API errors?**
- Check all API keys are correct
- Verify database and redis services are green
- Check service logs
