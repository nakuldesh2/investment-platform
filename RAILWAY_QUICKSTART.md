# Railway Deployment - Quick Start

**Goal:** Deploy the Investment Platform to Railway with public URL and allowlist protection.

## 5-Minute Quick Setup

### 1. Prerequisites ✓
- GitHub account (repository pushed)
- Railway account (free: https://railway.app)
- API keys from: Alpha Vantage, MarketAux, NewsAPI, Finnhub

### 2. Connect GitHub to Railway

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub"
4. Authorize Railway & select `investment-platform` repository
5. Railway automatically detects `docker-compose.yml` and starts deployment

### 3. Auto-Created Services

Railway will create:
- ✅ PostgreSQL Database
- ✅ Redis Cache  
- ✅ Gateway Service (API)
- ✅ Market Data Service
- ✅ News Service
- ✅ ML Signal Service
- ✅ Frontend Service (React)

### 4. Set Environment Variables

For each service, click "Variables" and add:

**Gateway Service:**
```
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=<generate_with: python3 -c "import secrets; print(secrets.token_urlsafe(32))">
ALLOWLIST_EMAILS=yourname@example.com,admin@example.com
JWT_EXPIRATION_HOURS=24
```

**Market Data Service:**
```
ENVIRONMENT=production
ALPHA_VANTAGE_API_KEY=<your_key>
```

**News Service:**
```
ENVIRONMENT=production
MARKETAUX_API_TOKEN=<your_key>
```

**Frontend Service:**
```
REACT_APP_BACKEND_URL=https://<gateway-domain>.railway.app
```

(Replace `<gateway-domain>` with the domain generated for gateway-service)

### 5. Get Public Domains

For each service, go to "Settings" → "Domains" → "Generate Domain":
- Gateway Service → Copy domain (this is your API endpoint)
- Frontend Service → Copy domain (this is your app URL)

### 6. Test It! 🚀

Open frontend domain in browser:
```
https://<your-frontend-domain>
```

**Test Flow:**
1. Click "Create Account"
2. Register with allowlisted email → Auto-login
3. Configure API keys
4. View dashboard with real market data
5. Logout and login

**Test Non-Allowlisted User:**
1. Register with different email → See "pending approval" message
2. Verify only allowlisted users can access

### 7. Custom Domain (Optional)

Add your own domain:
1. Gateway Service → Settings → Domains → "Add Custom Domain"
2. Add DNS CNAME record pointing to Railway endpoint
3. Wait for DNS propagation (5-30 minutes)

## Key Features Enabled ✓

| Feature | Status |
|---------|--------|
| User Registration | ✓ Working |
| Email Allowlist | ✓ Auto-approval |
| JWT Authentication | ✓ httpOnly Cookies |
| API Key Storage | ✓ Secure Database |
| Market Data | ✓ Real APIs |
| News & Sentiment | ✓ Real APIs |
| ML Signals | ✓ Generated |
| Public URL | ✓ Railway Domain |
| HTTPS | ✓ Automatic |
| Private (Allowlist) | ✓ Protected |

## Monitoring

View logs in Railway:
- Click service → "Logs" tab
- Filter by timestamp or error level
- Monitor deployment status

## Next Steps

1. Add your real API keys in Variables
2. Share frontend URL only with allowlisted users
3. Monitor usage in Railway dashboard
4. (Optional) Set up GitHub Actions for auto-deploy on push

## Troubleshooting

**Services won't start?**
- Check Railway Logs for errors
- Verify all environment variables are set
- Wait 2-3 minutes for database initialization

**Can't login?**
- Verify email is in ALLOWLIST_EMAILS
- Check gateway-service logs
- Try different browser/incognito mode

**Frontend can't reach API?**
- Verify REACT_APP_BACKEND_URL is correct
- Check it includes `https://`
- Test API directly: `curl https://<gateway>/health`

**Database connection fails?**
- Railway PostgreSQL takes 2-3 min to initialize
- Database tables auto-created on first deployment
- Check gateway-service startup logs

## Important Notes

⚠️ **Security:**
- Generate unique JWT SECRET_KEY for production
- Change ALLOWLIST_EMAILS to your emails
- Never commit real API keys to GitHub
- Use Railway Variables panel for sensitive data

⚠️ **Data:**
- PostgreSQL data persists with Railway volumes
- Redis cache resets on redeployment
- Regular backups recommended (Railway offers premium backup)

## Full Documentation

For detailed setup and troubleshooting: See `DEPLOYMENT.md`

## Support

Railway Dashboard: https://railway.app
Railway Docs: https://docs.railway.app
Investment Platform Repo: https://github.com/nakuldesh2/investment-platform
