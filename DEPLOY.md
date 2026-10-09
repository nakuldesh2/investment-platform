# Deploy to Railway - Complete Guide

## Prerequisites (5 minutes)

### 1. Generate Secret Key
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```
**Save the output.**

### 2. Get API Keys
- **Alpha Vantage:** https://www.alphavantage.co/ (free)
- **MarketAux:** https://www.marketaux.com/ (free)

### 3. Create Railway Account
Go to https://railway.app and sign up (free tier)

### 4. Know Your Email
This will be auto-approved to access the platform.

---

## Deploy (10 minutes)

### Step 1: Connect GitHub to Railway
1. Go to https://railway.app
2. Click **"New Project"**
3. Click **"Deploy from GitHub"**
4. Authorize Railway and select `investment-platform`
5. Wait 2-3 minutes for services to appear (postgres, redis, all 5 services)

### Step 2: Configure Gateway Service
1. Click on **gateway-service**
2. Click **"Variables"** tab
3. Add these variables:
```
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=<paste_from_step_1>
ALLOWLIST_EMAILS=yourname@example.com
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```
4. Click **"Save"** or **"Deploy"**

### Step 3: Configure Market Data Service
1. Click on **market-data-service**
2. Click **"Variables"** tab
3. Add:
```
ENVIRONMENT=production
ALPHA_VANTAGE_API_KEY=<your_key_from_prerequisites>
```
4. Click **"Save"**

### Step 4: Configure News Service
1. Click on **news-service**
2. Click **"Variables"** tab
3. Add:
```
ENVIRONMENT=production
MARKETAUX_API_TOKEN=<your_token_from_prerequisites>
```
4. Click **"Save"**

### Step 5: Configure ML Signal Service
1. Click on **ml-signal-service**
2. Click **"Variables"** tab
3. Add:
```
ENVIRONMENT=production
```
4. Click **"Save"**

### Step 6: Get Gateway Domain
1. Click on **gateway-service**
2. Click **"Settings"** tab
3. Scroll to **"Domains"**
4. Click **"Generate Domain"**
5. **Copy this domain** (you'll need it next)

### Step 7: Configure Frontend Service
1. Click on **frontend-service**
2. Click **"Variables"** tab
3. Add:
```
REACT_APP_BACKEND_URL=<paste_gateway_domain_from_step_6>
ENVIRONMENT=production
```
4. Click **"Save"**

### Step 8: Get Frontend Domain
1. Click on **frontend-service**
2. Click **"Settings"** tab
3. Scroll to **"Domains"**
4. Click **"Generate Domain"**
5. **Copy this domain** - This is your public URL! ✅

### Step 9: Wait for Services to Go Green
Go back to main dashboard and wait 5-10 minutes for all services to show green status:
- postgres ✅
- redis ✅
- gateway-service ✅
- market-data-service ✅
- news-service ✅
- ml-signal-service ✅
- frontend-service ✅

### Step 10: Test Your Platform
1. Open browser: `https://<your-frontend-domain>`
2. Click **"Create Account"**
3. Enter your email and password
4. Should auto-login (because email is in allowlist)
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

**Share the frontend URL with allowlisted users only.**

---

## Troubleshooting

**Services still red after 10 minutes?**
- Click service → "Logs" tab → check for errors
- Wait another 5 minutes

**Can't reach frontend?**
- Check domain was generated (Step 8)
- Try refreshing browser
- Wait 2-3 minutes for DNS

**Login fails?**
- Make sure email is in ALLOWLIST_EMAILS
- Check password is correct
- Try incognito window

**API returns errors?**
- Check API keys are correct
- Check key has calls remaining
- Wait 1 minute and retry
