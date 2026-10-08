# Public Deployment Implementation Guide

## Current Status
✅ **Phase 1 (50% Complete)**
- User model updated with allowlist fields
- Admin routes created
- Foundation in place for API key management

---

## Remaining Implementation Steps

### **Phase 1 Completion: API Key Management**

#### Step 1: Update Config for Allowlist Emails
**File:** `gateway-service/app/config.py`

Add to `GatewaySettings` class:
```python
allowlist_emails: list = Field(
    default=["admin@example.com"],
    description="List of emails allowlisted to register without approval"
)
```

**Update .env.example:**
```
ALLOWLIST_EMAILS=admin@example.com,user1@example.com,user2@example.com
```

#### Step 2: Update Auth Login to Check Allowlist
**File:** `gateway-service/app/routes/auth.py` - Update login function (line 58+)

Add check before JWT generation:
```python
# Check if user is approved/allowlisted
if not user.is_allowlisted or user.status != "approved":
    logger.warning(f"Login attempt by non-approved user: {user.email}")
    raise UnauthorizedError("Your account is pending approval. Contact admin.")
```

#### Step 3: Create User API Keys Endpoints
**File:** `gateway-service/app/routes/auth.py` - Add new endpoint

```python
@router.get("/user-keys")
async def get_user_keys(request: Request, db: AsyncSession = Depends(get_db)):
    """Get current user's stored API keys (for frontend to use)"""
    user_id = request.state.user_id
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise UnauthorizedError("User not found")
    
    return {"api_keys": user.api_keys or {}}

@router.post("/user-keys")
async def update_user_keys(
    keys: dict,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Update current user's API keys"""
    user_id = request.state.user_id
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise UnauthorizedError("User not found")
    
    # Validate keys (optional - verify they work with external APIs)
    user.api_keys = keys
    await db.commit()
    
    return {"message": "API keys updated", "keys_stored": list(keys.keys())}
```

#### Step 4: Frontend API Key Setup Component
**File:** `frontend-service/src/components/ApiKeySetup.js` (REWRITE)

```javascript
import React, { useState } from "react";
import { authAPI } from "../api/client";
import "./ApiKeySetup.css";

export default function ApiKeySetup() {
  const [keys, setKeys] = useState({
    alpha_vantage: "",
    news_api: "",
    finnhub: ""
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const handleChange = (e) => {
    const { name, value } = e.target;
    setKeys(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setMessage("");

    try {
      // Validate keys with external APIs before saving
      // This is optional but recommended
      
      // Save keys
      const response = await fetch(`${window.API_BASE || "http://localhost:8000"}/auth/user-keys`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(keys)
      });

      if (!response.ok) {
        throw new Error("Failed to save API keys");
      }

      setMessage("✅ API keys saved successfully!");
      setKeys({ alpha_vantage: "", news_api: "", finnhub: "" });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="api-key-setup">
      <h2>Configure API Keys</h2>
      <p>Enter your API keys to fetch real market data</p>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Alpha Vantage API Key</label>
          <input
            type="password"
            name="alpha_vantage"
            value={keys.alpha_vantage}
            onChange={handleChange}
            placeholder="Get from alphavantage.co"
            required
          />
          <small>Free tier: 5 calls/min, 500/day</small>
        </div>

        <div className="form-group">
          <label>NewsAPI Key</label>
          <input
            type="password"
            name="news_api"
            value={keys.news_api}
            onChange={handleChange}
            placeholder="Get from newsapi.org"
            required
          />
          <small>Free tier: 100 requests/day</small>
        </div>

        <div className="form-group">
          <label>Finnhub API Key</label>
          <input
            type="password"
            name="finnhub"
            value={keys.finnhub}
            onChange={handleChange}
            placeholder="Get from finnhub.io"
            required
          />
          <small>Free tier: 60 calls/min</small>
        </div>

        {error && <div className="error">{error}</div>}
        {message && <div className="success">{message}</div>}

        <button type="submit" disabled={loading}>
          {loading ? "Saving..." : "Save API Keys"}
        </button>
      </form>

      <div className="help-section">
        <h3>How to get API keys:</h3>
        <ul>
          <li><a href="https://www.alphavantage.co/api/" target="_blank">Alpha Vantage</a></li>
          <li><a href="https://newsapi.org/" target="_blank">NewsAPI</a></li>
          <li><a href="https://finnhub.io/" target="_blank">Finnhub</a></li>
        </ul>
      </div>
    </div>
  );
}
```

---

### **Phase 2: Real API Integration**

#### Step 1: Update Market Data Service
**File:** `market-data-service/app/main.py` - Replace mock logic

```python
async def get_quote(symbol: str, api_key: str = Header(None)):
    """Get real stock quote"""
    if not api_key:
        raise UnauthorizedError("API key required. Header: X-Alpha-Vantage-Key")
    
    normalized_symbol = symbol.upper()
    
    # Check cache first
    cached = await check_cache(normalized_symbol, db)
    if cached and not cached.is_expired():
        return cached
    
    # Call real Alpha Vantage API
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": normalized_symbol,
        "apikey": api_key
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get("https://www.alphavantage.co/query", params=params)
        data = response.json()
    
    # Handle rate limits gracefully
    if "Note" in data or "Information" in data:
        # Return cached data if available, else error
        raise RateLimitError("API rate limit exceeded")
    
    # Parse and cache result
    quote = parse_quote(data.get("Global Quote", {}))
    await cache_quote(quote, db)
    
    return quote
```

#### Step 2: Add Rate Limit Handling
**File:** `market-data-service/app/services/rate_limiter.py` (NEW)

```python
import asyncio
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, calls_per_minute: int):
        self.calls_per_minute = calls_per_minute
        self.call_times = []
    
    async def wait_if_needed(self):
        now = datetime.utcnow()
        # Remove calls older than 1 minute
        self.call_times = [t for t in self.call_times if (now - t).seconds < 60]
        
        if len(self.call_times) >= self.calls_per_minute:
            wait_time = 60 - (now - self.call_times[0]).seconds
            if wait_time > 0:
                await asyncio.sleep(wait_time)
                self.call_times = []
        
        self.call_times.append(now)

# Usage in routes
alpha_limiter = RateLimiter(5)  # Alpha Vantage: 5 calls/min

@app.get("/quote/{symbol}")
async def get_quote(symbol: str):
    await alpha_limiter.wait_if_needed()
    # ... call API
```

#### Step 3: Update News Service
Similar pattern for NewsAPI and Finnhub - accept keys from headers, call real APIs, implement caching.

---

### **Phase 3: Frontend Updates**

#### Step 1: Create Request Access Component
**File:** `frontend-service/src/components/RequestAccess.js` (NEW)

```javascript
export default function RequestAccess({ email }) {
  const [submitted, setSubmitted] = useState(false);

  const handleRequest = async () => {
    // Send request to backend
    await fetch("/auth/request-access", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email })
    });
    setSubmitted(true);
  };

  return (
    <div className="request-access">
      <h2>Access Pending</h2>
      <p>Your account ({email}) is pending admin approval.</p>
      <p>Check back later or contact admin for access.</p>
      {!submitted && <button onClick={handleRequest}>Request Access</button>}
      {submitted && <p>✅ Request sent to admin</p>}
    </div>
  );
}
```

#### Step 2: Update App.js to Show API Setup
**File:** `frontend-service/src/App.js`

```javascript
import ApiKeySetup from "./components/ApiKeySetup";

// Add to Dashboard or create a Settings page
if (!userHasApiKeys) {
  return <ApiKeySetup />;
}
```

#### Step 3: Update API Client to Pass Keys in Headers
**File:** `frontend-service/src/api/client.js`

```javascript
// Add interceptor to include API keys in all requests
client.interceptors.request.use((config) => {
  const keys = sessionStorage.getItem("api_keys");
  if (keys) {
    const parsedKeys = JSON.parse(keys);
    config.headers["X-Alpha-Vantage-Key"] = parsedKeys.alpha_vantage;
    config.headers["X-News-API-Key"] = parsedKeys.news_api;
    config.headers["X-Finnhub-Key"] = parsedKeys.finnhub;
  }
  return config;
});
```

---

### **Phase 4: Public Deployment**

#### Step 1: Choose Deployment Platform
**Option 1: Railway** (Recommended - easiest)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Create project
railway init

# Deploy
railway up
```

**Option 2: Render**
- Sign up at render.com
- Create new PostgreSQL database
- Deploy docker-compose services
- Set environment variables

#### Step 2: Create Production Docker Compose
**File:** `docker-compose.prod.yml` (NEW)

```yaml
version: '3.9'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    # Use managed database from Railway/Render instead
    # DATABASE_URL will be provided by platform

  gateway-service:
    build: ./gateway-service
    environment:
      DATABASE_URL: ${DATABASE_URL}
      ENVIRONMENT: production
      SECRET_KEY: ${SECRET_KEY}
      LOG_LEVEL: INFO
    ports:
      - "8000:8000"
    depends_on:
      - postgres

  market-data-service:
    build: ./market-data-service
    environment:
      DATABASE_URL: ${DATABASE_URL}
      ENVIRONMENT: production
    ports:
      - "8001:8001"

  # Similar for news-service, ml-signal-service

  frontend:
    build: ./frontend-service
    environment:
      REACT_APP_BACKEND_URL: ${BACKEND_URL}
    ports:
      - "3000:80"
```

#### Step 3: Set Environment Variables on Platform
```
DATABASE_URL=postgresql://...
SECRET_KEY=<generate-random-key>
ALLOWLIST_EMAILS=your-email@example.com
BACKEND_URL=https://your-domain.com
ENVIRONMENT=production
```

---

### **Phase 5: CI/CD Pipeline**

#### Step 1: Create GitHub Actions Workflow
**File:** `.github/workflows/deploy.yml` (NEW)

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          pip install -r requirements.txt
          pytest --cov

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Railway
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: |
          npm install -g @railway/cli
          railway up --service gateway-service
          railway up --service market-data-service
          railway up --service news-service
          railway up --service ml-signal-service
```

---

## Quick Reference: What's Running Now ✅

```
Docker containers (local):
- gateway-service: http://localhost:8000
- market-data-service: http://localhost:8001
- news-service: http://localhost:8002
- ml-signal-service: http://localhost:8003
- PostgreSQL: localhost:5432
- Redis: localhost:6379

Git status:
- Latest commit: Add public deployment infrastructure
- Branch: main
- 3 files changed (User model + admin routes)
```

---

## Next Session: Start With

```bash
cd /Users/nakuldeshpande/Downloads/investment-platform

# Phase 1 Completion (2 hours)
1. Update gateway-service/app/config.py - add ALLOWLIST_EMAILS
2. Update gateway-service/app/routes/auth.py - add login allowlist check + key endpoints
3. Rewrite frontend-service/src/components/ApiKeySetup.js
4. Update .env.example

# Phase 2 (4 hours)
5. Update market-data-service/app/main.py - use real APIs
6. Update news-service/app/main.py - use real APIs
7. Add rate limiting service layer
8. Test with real API keys

# Phase 3 (3 hours)
9. Create Request Access component
10. Update App.js for API key setup flow
11. Update API client headers

# Phase 4 (3 hours)
12. Sign up for Railway/Render
13. Deploy services
14. Configure domain + HTTPS

# Phase 5 (2 hours)
15. Create GitHub Actions CI/CD
16. Enable auto-deploy on git push
17. Test end-to-end with real data

# Final
18. Commit all changes
19. Push to GitHub
20. Share public URL
```

---

## Key Files to Know

| File | Purpose | Status |
|------|---------|--------|
| `gateway-service/app/models/user.py` | User allowlist model | ✅ Updated |
| `gateway-service/app/routes/admin.py` | Admin approval endpoints | ✅ Created |
| `gateway-service/app/config.py` | Config with allowlist | ⏳ Update needed |
| `market-data-service/app/main.py` | Real API calls | ⏳ Update needed |
| `frontend-service/src/components/ApiKeySetup.js` | User API key form | ⏳ Rewrite needed |
| `docker-compose.prod.yml` | Production deployment | ⏳ Create needed |
| `.github/workflows/deploy.yml` | CI/CD pipeline | ⏳ Create needed |

---

## Success Criteria

✅ User can register and allowlisted users auto-approved  
✅ Non-allowlisted users see "pending approval" message  
✅ Users can enter/manage their own API keys  
✅ Real market data fetched from Alpha Vantage  
✅ Real news data fetched from NewsAPI/Finnhub  
✅ Website accessible at public URL  
✅ Only allowlisted users can access  
✅ API limits respected with rate limiting & caching  
✅ Auto-deployment on git push  
✅ Real-time market updates on dashboard  

---

## Estimated Total Time
- Phase 1 Completion: 2 hours
- Phase 2: 4 hours
- Phase 3: 3 hours
- Phase 4: 3 hours
- Phase 5: 2 hours
- **Total: 14 hours**

Current: Phase 1 is 50% complete. Continue from Phase 1 completion in next session.
