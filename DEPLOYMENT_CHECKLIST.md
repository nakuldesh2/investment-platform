# Deployment Checklist - Investment Platform on Railway

Use this checklist to ensure your deployment is complete and properly configured.

## Pre-Deployment ✓

- [ ] GitHub repository is public and accessible
- [ ] All code is committed and pushed to `main` branch
- [ ] `.env` file is NOT committed (should be in `.gitignore`)
- [ ] `CLAUDE.md` exists with project documentation
- [ ] `docker-compose.yml` is in project root
- [ ] All services have Dockerfile (market-data, news, ml-signal, gateway, frontend)
- [ ] Repository is pushed to GitHub: `git push origin main`

## Railway Account Setup ✓

- [ ] Railway account created at https://railway.app
- [ ] GitHub account authorized with Railway
- [ ] Billing method added (free tier has usage limits)
- [ ] Email verified on Railway account

## Deployment ✓

### Connect Repository
- [ ] New Project created in Railway
- [ ] GitHub repository connected
- [ ] `docker-compose.yml` detected automatically
- [ ] Services showing in Railway dashboard:
  - [ ] gateway-service
  - [ ] market-data-service
  - [ ] news-service
  - [ ] ml-signal-service
  - [ ] frontend-service
  - [ ] postgres (database)
  - [ ] redis (cache)

### Database Setup
- [ ] PostgreSQL service created and healthy
- [ ] Redis service created and healthy
- [ ] Database `investment_platform` initialized
- [ ] Tables auto-created on first deployment:
  - [ ] users
  - [ ] cached_quotes
  - [ ] cached_news
  - [ ] cached_signals

## Environment Configuration ✓

### Gateway Service Variables
- [ ] `ENVIRONMENT=production`
- [ ] `DEBUG=False`
- [ ] `LOG_LEVEL=INFO`
- [ ] `SECRET_KEY=<unique_32char_key>` (generated)
- [ ] `JWT_ALGORITHM=HS256`
- [ ] `JWT_EXPIRATION_HOURS=24`
- [ ] `ALLOWLIST_EMAILS=<your_emails>` (comma-separated)
- [ ] `SERVICE_NAME=gateway-service`
- [ ] `SERVICE_PORT=8000`
- [ ] `REQUEST_TIMEOUT_SECONDS=30`
- [ ] `MARKET_DATA_BASE_URL=http://market-data-service:8001`
- [ ] `NEWS_SERVICE_BASE_URL=http://news-service:8002`
- [ ] `ML_SIGNAL_BASE_URL=http://ml-signal-service:8003`
- [ ] `DATABASE_URL` (auto-set by Railway)
- [ ] `REDIS_URL` (auto-set by Railway)

### Market Data Service Variables
- [ ] `ENVIRONMENT=production`
- [ ] `DEBUG=False`
- [ ] `LOG_LEVEL=INFO`
- [ ] `ALPHA_VANTAGE_API_KEY=<your_key>`
- [ ] `SERVICE_NAME=market-data-service`
- [ ] `SERVICE_PORT=8001`
- [ ] `REQUEST_TIMEOUT_SECONDS=30`

### News Service Variables
- [ ] `ENVIRONMENT=production`
- [ ] `DEBUG=False`
- [ ] `LOG_LEVEL=INFO`
- [ ] `MARKETAUX_API_TOKEN=<your_key>`
- [ ] `SERVICE_NAME=news-service`
- [ ] `SERVICE_PORT=8002`
- [ ] `REQUEST_TIMEOUT_SECONDS=30`

### ML Signal Service Variables
- [ ] `ENVIRONMENT=production`
- [ ] `DEBUG=False`
- [ ] `LOG_LEVEL=INFO`
- [ ] `SERVICE_NAME=ml-signal-service`
- [ ] `SERVICE_PORT=8003`
- [ ] `REQUEST_TIMEOUT_SECONDS=30`

### Frontend Service Variables
- [ ] `ENVIRONMENT=production`
- [ ] `DEBUG=False`
- [ ] `REACT_APP_BACKEND_URL=https://<gateway_public_domain>`

## Domain Assignment ✓

### Public Domains
- [ ] Gateway Service domain generated:
  - [ ] Format: `https://<service-name>.up.railway.app`
  - [ ] Save this domain - it's your API endpoint
  
- [ ] Frontend Service domain generated:
  - [ ] Format: `https://<service-name>.up.railway.app`
  - [ ] This is where users access the UI

### Custom Domain (Optional)
- [ ] Custom domain purchased and ready
- [ ] DNS CNAME record created pointing to Railway endpoint
- [ ] DNS propagation verified (use online DNS checker)
- [ ] Custom domain assigned in Railway dashboard
- [ ] SSL certificate provisioned by Railway

## Deployment Status ✓

### Service Deployment
- [ ] Gateway Service: **Running** (deployment successful)
- [ ] Market Data Service: **Running**
- [ ] News Service: **Running**
- [ ] ML Signal Service: **Running**
- [ ] Frontend Service: **Running**
- [ ] PostgreSQL Database: **Healthy**
- [ ] Redis Cache: **Healthy**

### First Deployment Logs
- [ ] No critical errors in gateway-service logs
- [ ] Database initialization message in logs
- [ ] All services listening on correct ports

## Testing ✓

### Health Checks
```bash
# Test gateway health (replace with your domain)
curl https://<gateway-domain>/health

# Should return:
# {
#   "status": "ok",
#   "service": "gateway-service",
#   "downstreams": {...}
# }
```
- [ ] Gateway health check passes

### Authentication Flow

#### Register Non-Allowlisted User
```bash
curl -X POST https://<gateway-domain>/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'
```
- [ ] Returns: `"status":"pending"`
- [ ] User cannot login (rejection message)

#### Register Allowlisted User
```bash
curl -X POST https://<gateway-domain>/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"<allowlisted-email>","password":"securepass123"}'
```
- [ ] Returns: `"status":"approved"`

#### Login
```bash
curl -X POST https://<gateway-domain>/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"email":"<allowlisted-email>","password":"securepass123"}'
```
- [ ] Returns JWT token
- [ ] Sets httpOnly cookie

#### Get User Info
```bash
curl https://<gateway-domain>/auth/me \
  -b cookies.txt
```
- [ ] Returns user info with status

#### API Key Management
```bash
curl -X POST https://<gateway-domain>/auth/user-keys \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"alpha_vantage":"key1","news_api":"key2","finnhub":"key3"}'
```
- [ ] API keys saved successfully

### Frontend Testing

1. **Open Frontend URL**
   - [ ] Frontend loads without errors
   - [ ] Can reach in browser: `https://<frontend-domain>`

2. **Login Screen**
   - [ ] Title: "Sign In" / "Create Account" visible
   - [ ] Email and password fields present
   - [ ] Toggle between Sign In / Create Account works

3. **Register Flow (Non-Allowlisted)**
   - [ ] Switch to "Create Account"
   - [ ] Register with new email
   - [ ] See "Access Request Pending" message
   - [ ] "Check Status" button works

4. **Register Flow (Allowlisted)**
   - [ ] Register with allowlisted email
   - [ ] Auto-login happens
   - [ ] Redirected to API Key Setup page
   - [ ] Can enter API keys
   - [ ] Keys saved successfully

5. **Dashboard**
   - [ ] After API keys, see Dashboard page
   - [ ] Market Data tab shows stock quote
   - [ ] News & Sentiment tab shows news
   - [ ] AI Signals tab shows signals
   - [ ] Logout button works

## Security Verification ✓

### Token Security
- [ ] JWT token stored in httpOnly cookie (check browser DevTools)
- [ ] Token NOT in localStorage
- [ ] Token NOT in sessionStorage
- [ ] No secrets in frontend code

### Database
- [ ] User passwords hashed with bcrypt
- [ ] API keys encrypted in database (if applicable)
- [ ] No plaintext passwords in logs
- [ ] No API keys in logs

### HTTPS
- [ ] All endpoints use HTTPS
- [ ] Browser shows padlock icon
- [ ] Mixed content warnings: NONE
- [ ] SSL certificate valid

### Access Control
- [ ] Non-allowlisted users blocked from login
- [ ] Pending users can't access API
- [ ] Approved users can access all features
- [ ] JWT expiration works (wait 24 hours or modify in testing)
- [ ] Logout clears cookie properly

## Performance & Monitoring ✓

### Railway Dashboard
- [ ] View real-time logs for each service
- [ ] Monitor CPU/Memory usage
- [ ] Check deployment status and history
- [ ] View billing/usage metrics

### Error Monitoring
- [ ] No 5xx errors in gateway logs
- [ ] Database connections stable
- [ ] Redis cache operational
- [ ] External API failures handled gracefully

## Documentation ✓

- [ ] Updated CLAUDE.md with deployment instructions
- [ ] DEPLOYMENT.md covers all steps
- [ ] RAILWAY_QUICKSTART.md has 5-minute guide
- [ ] README.md links to deployment guides
- [ ] API documentation current
- [ ] Troubleshooting guide complete

## Post-Deployment ✓

- [ ] Share frontend URL with allowlisted users only
- [ ] Keep SECRET_KEY safe (not shared)
- [ ] Monitor logs regularly for errors
- [ ] Set up email notifications for deployments
- [ ] Plan for regular backups (if needed)
- [ ] Document custom domain setup (if used)

## Optional Enhancements ✓

- [ ] GitHub Actions for auto-deploy on push
- [ ] Analytics/monitoring service (Sentry, etc.)
- [ ] Email notifications for errors
- [ ] API rate limiting per user
- [ ] User management dashboard
- [ ] Audit logging for user actions

## Rollback Procedure (If Needed)

1. Go to Railway dashboard → Deployments
2. Find previous stable deployment
3. Click "Redeploy"
4. All services revert to previous version
5. Verify deployment is healthy

## Support & Resources

| Resource | Link |
|----------|------|
| Railway Docs | https://docs.railway.app |
| Investment Platform Repo | https://github.com/nakuldesh2/investment-platform |
| GitHub Issues | https://github.com/nakuldesh2/investment-platform/issues |
| CLAUDE.md | See project root |
| DEPLOYMENT.md | Detailed setup guide |

## Sign-Off ✓

- [ ] Deployment Date: _______________
- [ ] Deployed By: _______________
- [ ] All checklist items completed
- [ ] Frontend URL: _______________
- [ ] API Gateway URL: _______________
- [ ] Allowlist Emails: _______________
- [ ] Known Issues: _______________

---

**Ready to deploy!** 🚀

If any items are unchecked, go back and complete them before considering deployment complete.
