# Deploy to Render.com - Complete Free Guide

**Render is completely FREE with NO service limits. Perfect for your platform!**

---

## Prerequisites (10 minutes)

### 1. Generate Secret Key
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```
**Save the output.** You'll need it in Step 3.

### 2. Get API Keys (Free)
- **Alpha Vantage:** https://www.alphavantage.co/ → Get Free API Key
- **MarketAux:** https://www.marketaux.com/ → Try Free → Sign up

### 3. Create Render Account
Go to https://render.com and click **"Sign Up"**
- Use GitHub login (easiest)
- Authorize Render to access your GitHub repos

---

## Deploy (30 minutes)

### Step 1: Create First Service (Gateway)

1. Go to https://render.com/dashboard
2. Click **"New +"** → **"Web Service"**
3. **Select repository:** `investment-platform`
4. **Name:** `gateway-service`
5. **Environment:** `Docker`
6. **Region:** `Ohio` (or your closest)
7. Click **"Create Web Service"**

### Step 2: Configure Gateway Service

Wait for page to load, then:

1. Click **"Environment"** tab
2. Add these variables:

```
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=<paste_your_secret_key>
ALLOWLIST_EMAILS=<your_email@example.com>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
SERVICE_NAME=gateway-service
SERVICE_PORT=8000
REQUEST_TIMEOUT_SECONDS=30
MARKET_DATA_BASE_URL=http://market-data-service:8001
NEWS_SERVICE_BASE_URL=http://news-service:8002
ML_SIGNAL_BASE_URL=http://ml-signal-service:8003
DATABASE_URL=postgresql://<user>:<password>@<host>:<port>/<database>
REDIS_URL=redis://<host>:<port>
```

3. Click **"Settings"** tab → Scroll to **"Build Command"**
4. Enter:
```
cd gateway-service && pip install -r requirements.txt
```

5. Scroll to **"Start Command"**
6. Enter:
```
cd gateway-service && uvicorn app.main:app --host 0.0.0.0 --port 8000
```

7. Click **"Save Changes"** → Wait for deployment (takes ~5-10 minutes)

### Step 3: Create PostgreSQL Database

1. Click **"New +"** → **"PostgreSQL"**
2. **Name:** `investment-db`
3. Click **"Create Database"**
4. Wait for it to create (2-3 minutes)
5. Click on the database → **"Connect"** → Copy the **Internal Database URL**
6. Save this URL - you'll use it for all services

### Step 4: Create Redis Cache

1. Click **"New +"** → **"Redis"**
2. **Name:** `investment-cache`
3. Click **"Create Redis"**
4. Wait for creation (2-3 minutes)
5. Click on Redis → **"Connect"** → Copy the **Internal Redis URL**
6. Save this URL

### Step 5: Create Market Data Service

1. Click **"New +"** → **"Web Service"**
2. **Repository:** `investment-platform`
3. **Name:** `market-data-service`
4. **Environment:** `Docker`
5. **Create Web Service**

Configure it:
1. **Environment** tab → Add:
```
ENVIRONMENT=production
DEBUG=False
ALPHA_VANTAGE_API_KEY=<your_api_key>
SERVICE_NAME=market-data-service
SERVICE_PORT=8001
REQUEST_TIMEOUT_SECONDS=30
```

2. **Settings** tab:
   - Build Command: `cd market-data-service && pip install -r requirements.txt`
   - Start Command: `cd market-data-service && uvicorn app.main:app --host 0.0.0.0 --port 8001`

3. Click **"Save Changes"**

### Step 6: Create News Service

1. Click **"New +"** → **"Web Service"**
2. **Repository:** `investment-platform`
3. **Name:** `news-service`
4. **Environment:** `Docker`
5. **Create Web Service**

Configure it:
1. **Environment** tab → Add:
```
ENVIRONMENT=production
DEBUG=False
MARKETAUX_API_TOKEN=<your_token>
SERVICE_NAME=news-service
SERVICE_PORT=8002
REQUEST_TIMEOUT_SECONDS=30
```

2. **Settings** tab:
   - Build Command: `cd news-service && pip install -r requirements.txt`
   - Start Command: `cd news-service && uvicorn app.main:app --host 0.0.0.0 --port 8002`

3. Click **"Save Changes"**

### Step 7: Create ML Signal Service

1. Click **"New +"** → **"Web Service"**
2. **Repository:** `investment-platform`
3. **Name:** `ml-signal-service`
4. **Environment:** `Docker`
5. **Create Web Service**

Configure it:
1. **Environment** tab → Add:
```
ENVIRONMENT=production
DEBUG=False
SERVICE_NAME=ml-signal-service
SERVICE_PORT=8003
REQUEST_TIMEOUT_SECONDS=30
```

2. **Settings** tab:
   - Build Command: `cd ml-signal-service && pip install -r requirements.txt`
   - Start Command: `cd ml-signal-service && uvicorn app.main:app --host 0.0.0.0 --port 8003`

3. Click **"Save Changes"**

### Step 8: Create Frontend Service

1. Click **"New +"** → **"Web Service"**
2. **Repository:** `investment-platform`
3. **Name:** `frontend-service`
4. **Environment:** `Docker`
5. **Create Web Service**

Configure it:
1. **Environment** tab → Add:
```
REACT_APP_BACKEND_URL=https://<gateway-service-url>.onrender.com
ENVIRONMENT=production
DEBUG=False
```
(You'll get the gateway URL after it deploys - come back and update this)

2. **Settings** tab:
   - Build Command: `cd frontend-service && npm install && npm run build`
   - Start Command: `cd frontend-service && npm start`

3. Click **"Save Changes"**

### Step 9: Update All Services with Database URLs

Go back to each service and update **Environment** with:

```
DATABASE_URL=<paste_the_postgres_url_from_step_3>
REDIS_URL=<paste_the_redis_url_from_step_4>
```

**For Gateway Service:** Also update:
```
MARKET_DATA_BASE_URL=https://market-data-service-xxx.onrender.com
NEWS_SERVICE_BASE_URL=https://news-service-xxx.onrender.com
ML_SIGNAL_BASE_URL=https://ml-signal-service-xxx.onrender.com
```

(Replace `xxx` with actual Render URLs from each service)

### Step 10: Get Public URLs

For each service, click on it and look for the **URL** at the top. Examples:
- **Gateway:** `https://gateway-service-abc123.onrender.com`
- **Frontend:** `https://frontend-service-abc123.onrender.com`

**Save the Gateway URL and update Frontend's `REACT_APP_BACKEND_URL`**

### Step 11: Wait for All Services to Deploy

1. Go to **Dashboard**
2. Check each service status (should show green "Running")
3. Wait 10-15 minutes for all to be active

Services to see:
- ✅ gateway-service
- ✅ market-data-service
- ✅ news-service
- ✅ ml-signal-service
- ✅ frontend-service
- ✅ investment-db
- ✅ investment-cache

### Step 12: Test Your Platform

1. Open **Frontend URL** in browser: `https://frontend-service-xxx.onrender.com`
2. Click **"Create Account"**
3. Enter your email and password
4. Should auto-login (email is in allowlist)
5. Configure API keys
6. View dashboard with real market data

---

## Complete! 🎉

Your platform is now:
- ✅ **Live on public HTTPS**
- ✅ **Protected by allowlist**
- ✅ **Using real market data**
- ✅ **Cost: $0/month (forever)**

**Share the Frontend URL only with allowlisted users.**

---

## Troubleshooting

**Service shows "Deploy failed"?**
- Click service → **"Logs"** → Check error messages
- Common: Missing environment variable
- Common: Build command path is wrong

**Can't reach frontend?**
- Check service is "Running" (not "Building")
- Wait 5 more minutes (first deploy is slow)
- Clear browser cache and refresh

**Login fails?**
- Verify email is in `ALLOWLIST_EMAILS`
- Check gateway-service logs for errors
- Try incognito window

**API errors?**
- Verify all `DATABASE_URL` and `REDIS_URL` are set
- Check database and redis services are running
- Verify API keys are correct

---

## Next Steps (After Deployment)

- Monitor services in Render dashboard
- Scale up if needed (just increase instance size - still free tier!)
- Add more users to allowlist
- Customize the allowlist in gateway-service environment
