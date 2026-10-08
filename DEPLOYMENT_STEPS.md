# 🚀 Step-by-Step Deployment Guide

Follow this exactly. Copy-paste each command. Takes ~40 minutes.

---

## STEP 1: Get Your API Keys (5 minutes)

### Alpha Vantage (Real Stock Data)
1. Go to https://www.alphavantage.co/
2. Click "GET FREE API KEY"
3. Enter your email
4. Copy the API key
5. Save it: `ALPHA_VANTAGE_API_KEY=_______________`

### MarketAux (Real News Data)
1. Go to https://www.marketaux.com/
2. Click "Try Free"
3. Sign up with email
4. Verify email
5. Copy your API token
6. Save it: `MARKETAUX_API_TOKEN=_______________`

---

## STEP 2: Generate JWT Secret Key (1 minute)

Open Terminal and run:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Copy the output. You'll need it in a few minutes.**

Example output:
```
Lk5-7K_j8mN9pQ2rS3tU4vW5xY6zZ7aB8cD
```

---

## STEP 3: Go to Railway.app (2 minutes)

1. Open browser: https://railway.app
2. Click "Sign up with GitHub"
3. Authorize Railway
4. You're logged in

---

## STEP 4: Create New Project (5 minutes)

In Railway Dashboard:

1. Click **"New Project"**
2. Select **"Deploy from GitHub"**
3. Authorize again if needed
4. **Search:** `investment-platform`
5. **Click:** `nakuldesh2/investment-platform`
6. **Branch:** `main`
7. **Click:** "Deploy"

**⏳ Wait 3-5 minutes for services to appear...**

You should see:
- postgres
- redis
- gateway-service
- market-data-service
- news-service
- ml-signal-service
- frontend-service

---

## STEP 5: Configure Gateway Service (3 minutes)

Click on **gateway-service** in Railway:

1. Click **"Variables"** tab
2. Add these variables (copy-paste exactly):

```
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
SECRET_KEY=<YOUR_SECRET_KEY_FROM_STEP_2>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
ALLOWLIST_EMAILS=<YOUR_EMAIL_ADDRESS>
SERVICE_NAME=gateway-service
SERVICE_PORT=8000
REQUEST_TIMEOUT_SECONDS=30
MARKET_DATA_BASE_URL=http://market-data-service:8001
NEWS_SERVICE_BASE_URL=http://news-service:8002
ML_SIGNAL_BASE_URL=http://ml-signal-service:8003
```

**⭐ Replace:**
- `<YOUR_SECRET_KEY_FROM_STEP_2>` with your actual key
- `<YOUR_EMAIL_ADDRESS>` with your email (for auto-approval)

3. Click **"Save"**

---

## STEP 6: Configure Market Data Service (2 minutes)

Click on **market-data-service**:

1. Click **"Variables"**
2. Add:

```
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
ALPHA_VANTAGE_API_KEY=<YOUR_ALPHA_VANTAGE_KEY>
SERVICE_NAME=market-data-service
SERVICE_PORT=8001
REQUEST_TIMEOUT_SECONDS=30
```

3. Click **"Save"**

---

## STEP 7: Configure News Service (2 minutes)

Click on **news-service**:

1. Click **"Variables"**
2. Add:

```
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
MARKETAUX_API_TOKEN=<YOUR_MARKETAUX_TOKEN>
SERVICE_NAME=news-service
SERVICE_PORT=8002
REQUEST_TIMEOUT_SECONDS=30
```

3. Click **"Save"**

---

## STEP 8: Configure ML Signal Service (1 minute)

Click on **ml-signal-service**:

1. Click **"Variables"**
2. Add:

```
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
SERVICE_NAME=ml-signal-service
SERVICE_PORT=8003
REQUEST_TIMEOUT_SECONDS=30
```

3. Click **"Save"**

---

## STEP 9: Get Gateway Domain (1 minute)

Click on **gateway-service**:

1. Click **"Settings"**
2. Scroll to **"Domains"**
3. Click **"Generate Domain"**
4. **COPY THIS DOMAIN. Save it.**

Example:
```
https://investment-platform-gateway.up.railway.app
```

---

## STEP 10: Configure Frontend (1 minute)

Click on **frontend-service**:

1. Click **"Variables"**
2. Add:

```
REACT_APP_BACKEND_URL=<GATEWAY_DOMAIN_FROM_STEP_9>
ENVIRONMENT=production
DEBUG=False
```

Replace with your actual gateway domain.

3. Click **"Save"**

---

## STEP 11: Get Frontend Domain (1 minute)

Click on **frontend-service**:

1. Click **"Settings"**
2. Scroll to **"Domains"**
3. Click **"Generate Domain"**
4. **COPY THIS. This is your public URL!**

Example:
```
https://investment-platform-frontend.up.railway.app
```

---

## STEP 12: Wait for Services (10 minutes)

All services should turn **GREEN**:
- [x] postgres
- [x] redis
- [x] gateway-service
- [x] market-data-service
- [x] news-service
- [x] ml-signal-service
- [x] frontend-service

If any are red, wait 2-3 more minutes.

---

## STEP 13: Test Gateway (1 minute)

Open Terminal and run:

```bash
curl https://investment-platform-gateway.up.railway.app/health
```

(Replace with YOUR gateway domain)

**Expected:** `{"status":"ok",...}`

---

## STEP 14: Register Test User (1 minute)

```bash
curl -X POST https://investment-platform-gateway.up.railway.app/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'
```

**Expected:** `{"id":1,"email":"test@example.com","status":"pending"}`

---

## STEP 15: Register Allowlisted User (1 minute)

Replace `your-email@example.com` with YOUR email:

```bash
curl -X POST https://investment-platform-gateway.up.railway.app/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"your-email@example.com","password":"testpass123"}'
```

**Expected:** `{"id":2,"email":"your-email@example.com","status":"approved"}`

---

## STEP 16: Open Frontend in Browser 🎉

Go to your frontend domain in browser:

```
https://investment-platform-frontend.up.railway.app
```

**You should see:**
- Login form
- "Sign In" heading
- Email and password fields
- "Create Account" button

---

## STEP 17: Register on Frontend (2 minutes)

1. Click **"Create Account"**
2. Enter your allowlisted email
3. Enter password: `testpass123`
4. Click **"Create Account"**

**What happens:**
- Auto-login
- Redirected to "Configure API Keys"

---

## STEP 18: Add API Keys (1 minute)

On "Configure API Keys" page:

1. Paste your **Alpha Vantage key**
2. Paste your **MarketAux token**
3. Leave **Finnhub** blank
4. Click **"Save API Keys"**

**What happens:**
- Success message
- Redirected to Dashboard

---

## STEP 19: Test Dashboard ✅ (1 minute)

You should see:
- Dashboard page
- "Investment Platform" title
- Navigation tabs (Market Data, News, Signals)
- Stock search box

**Test tabs:**
1. Enter "AAPL" in stock search
2. See real price, volume, change%
3. Click "News & Sentiment"
4. See real news articles
5. Click "AI Signals"
6. See signal rankings

---

## STEP 20: Test Non-Allowlisted User (1 minute)

In **new incognito/private** browser:

1. Go to same frontend URL
2. Click "Create Account"
3. Enter: `test@example.com` (NOT in allowlist)
4. Click "Create Account"

**Result:**
- See "Access Request Pending" page
- Cannot access dashboard

✅ **Allowlist protection working!**

---

## ✅ DEPLOYMENT COMPLETE! 🎉

**Everything is live:**
- ✅ Frontend URL: `https://investment-platform-frontend.up.railway.app`
- ✅ Gateway URL: `https://investment-platform-gateway.up.railway.app`
- ✅ Allowlist protection: ACTIVE
- ✅ Real market data: FLOWING
- ✅ Database: SECURE

**What's next:**
1. Share frontend URL with allowlisted users
2. They register with their emails
3. Auto-approved instantly
4. They see dashboard with real data

**Cost: $0/month** ✅
**Time to deploy: 40 minutes** ✅
**Status: PRODUCTION READY** ✅

Congratulations! 🚀

