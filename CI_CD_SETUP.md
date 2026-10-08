# CI/CD Pipeline Setup - GitHub Actions

This guide explains how to set up automated testing and deployment using GitHub Actions.

## Overview

The CI/CD pipeline automates:
- ✅ **Linting & Type Checking** - Python (Ruff, mypy), JavaScript (ESLint)
- ✅ **Unit & Integration Tests** - Python (pytest), JavaScript (Jest)
- ✅ **Docker Build Verification** - Ensure all services build
- ✅ **Automated Deployment** - Push to Railway on main branch merge
- ✅ **Notifications** - Slack alerts on success/failure

## Workflow Files

### 1. `.github/workflows/ci.yml` - Continuous Integration

Runs on **every push and pull request** to main/develop branches.

**Jobs:**
- `backend-lint`: Ruff + mypy for all Python services
- `backend-tests`: pytest with PostgreSQL/Redis services
- `frontend-lint`: npm build verification
- `docker-build`: Verify all Dockerfiles build successfully
- `ci-summary`: Summary of all checks

**Environment Setup:**
- PostgreSQL 15 test database
- Redis 7 test cache
- Python 3.11
- Node 18

**Coverage:**
- Runs pytest with coverage reports
- Uploads to Codecov.io
- Tests all 4 backend services
- Builds frontend
- Verifies Docker images

### 2. `.github/workflows/deploy.yml` - Deployment

Runs **automatically on merge to main** (or manual trigger).

**Steps:**
1. Install Railway CLI
2. Authenticate with Railway token
3. Deploy to Railway project
4. Wait 30 seconds for services to start
5. Health check gateway endpoint
6. Send Slack notification

**Requirements:**
- Railway project created
- Railway token saved as secret
- Slack webhook (optional)

## Setup Instructions

### Step 1: Enable GitHub Actions

1. Go to your repository on GitHub
2. Click "Settings" → "Actions" → "General"
3. Select "Allow all actions and reusable workflows"
4. Click "Save"

### Step 2: Create GitHub Secrets

Required secrets for deployment:

1. Go to "Settings" → "Secrets and variables" → "Actions"
2. Click "New repository secret"

**Required Secrets:**

#### `RAILWAY_TOKEN`
- Get from Railway dashboard
- Settings → "API Tokens"
- Create new token (copy full value)
- Scope: Full account access

#### `RAILWAY_PROJECT_ID`
- Get from Railway project URL
- URL format: `railway.app/project/{PROJECT_ID}`
- Copy the project ID

#### `RAILWAY_PUBLIC_URL` (Optional)
- Format: `https://gateway-service-prod.up.railway.app`
- Used for health check and notifications
- Can update after first deployment

#### `SLACK_WEBHOOK_URL` (Optional)
- For deployment notifications
- Create in Slack workspace: "Incoming Webhooks"
- App → "Create New App" → "From scratch"
- Features → "Incoming Webhooks"
- Add New Webhook to Workspace
- Copy the Webhook URL

**Setting Secrets:**
```
Name:  RAILWAY_TOKEN
Value: <railway_token_from_dashboard>

Name:  RAILWAY_PROJECT_ID
Value: <your_project_id>

Name:  RAILWAY_PUBLIC_URL
Value: https://gateway-service-prod.up.railway.app

Name:  SLACK_WEBHOOK_URL
Value: https://hooks.slack.com/services/T.../B.../...
```

### Step 3: Verify Workflow Files

Check that both workflow files exist:
```bash
ls -la .github/workflows/
# Should show: ci.yml, deploy.yml
```

### Step 4: Test CI Pipeline

1. Make a test commit and push:
```bash
git commit --allow-empty -m "test: trigger CI"
git push origin main
```

2. Go to GitHub repo → "Actions" tab
3. Should see workflow running
4. Wait for completion (3-5 minutes)
5. All checks should pass ✅

### Step 5: Test Deployment

1. Make another commit:
```bash
git commit --allow-empty -m "test: trigger deployment"
git push origin main
```

2. Go to "Actions" tab
3. Click "Deploy to Railway" workflow
4. Should see status:
   - ✅ Deploy to Railway (running)
   - After 2-3 min: Health check
   - After 5-10 min: Railway services restart
   - Slack notification sent

3. Check Railway dashboard to confirm services are healthy

## Workflow Triggers

### CI Workflow Triggers
- ✅ Push to `main` or `develop` branch
- ✅ Pull request to `main` or `develop`
- ❌ Does NOT deploy

### Deploy Workflow Triggers
- ✅ Push to `main` (after CI passes)
- ✅ Manual trigger via "Run workflow" button
- ❌ Does NOT run on develop or PR branches

## Understanding the Workflows

### CI Workflow (`.github/workflows/ci.yml`)

```
On: push to main/develop, or PR

├─ backend-lint
│  ├─ Install Python 3.11
│  ├─ Run Ruff (code style)
│  ├─ Run mypy (type checking)
│  └─ (continue on error)
│
├─ backend-tests
│  ├─ Start PostgreSQL service
│  ├─ Start Redis service
│  ├─ Run pytest for all services
│  ├─ Collect coverage reports
│  └─ Upload to Codecov
│
├─ frontend-lint
│  ├─ Install Node 18
│  ├─ npm install
│  ├─ npm run lint (if configured)
│  ├─ npm run build
│  └─ npm test (if configured)
│
├─ docker-build
│  └─ Build Docker image for each service (verify Dockerfile works)
│
└─ ci-summary
   └─ Report final status
```

**Duration:** 8-12 minutes

### Deploy Workflow (`.github/workflows/deploy.yml`)

```
On: push to main (after CI passes)

├─ Install Railway CLI
├─ Authenticate with Railway token
├─ Deploy to Railway project
├─ Wait 30 seconds
├─ Health check gateway
├─ Send Slack notification
└─ Done
```

**Duration:** 5-10 minutes (+ 2-5 min for services to restart)

## Customizing Workflows

### Add More Tests

Edit `.github/workflows/ci.yml`:

```yaml
- name: Run integration tests
  run: |
    pytest integration_tests/ -v --cov
```

### Change Deployment Trigger

Edit `.github/workflows/deploy.yml`:

```yaml
on:
  push:
    branches: [ main, production ]  # Deploy on both branches
  schedule:
    - cron: '0 2 * * *'  # Deploy daily at 2 AM UTC
```

### Add Manual Deployment Option

Already in deploy.yml:
```yaml
on:
  push:
    branches: [ main ]
  workflow_dispatch:  # Allows manual trigger
```

To manually trigger:
1. Go to "Actions" tab
2. Click "Deploy to Railway" workflow
3. Click "Run workflow" button
4. Select branch
5. Click "Run workflow"

## Monitoring Workflows

### View Workflow Status

1. Go to repository → "Actions" tab
2. Click workflow run to see details
3. View real-time logs for each job
4. See timing and resource usage

### Check Specific Job Logs

1. Click workflow run
2. Click job name (e.g., "backend-tests")
3. Expand each step to see output
4. Search for errors or warnings

### Workflow Artifacts

Some workflows generate artifacts:
- Coverage reports (XML)
- Build outputs
- Test results

Download from "Artifacts" section in workflow run.

## Troubleshooting

### Workflow not running?

- Check repository settings → Actions → "Allow all actions"
- Verify `.github/workflows/*.yml` files exist
- Check branch is `main` (only main triggers deploy)
- Look for syntax errors in YAML files

### Tests failing in CI but passing locally?

Common issues:
- Different environment variables
- Database not initialized in CI
- Missing test fixtures
- Race conditions in tests

Solution:
```bash
# Run tests same way as CI
python -m pip install -r requirements.txt
pytest --cov

# Use CI environment
export DATABASE_URL=postgresql+asyncpg://test:test@localhost:5432/test
export REDIS_URL=redis://localhost:6379/0
```

### Deployment stuck or failing?

1. Check Railway CLI authentication:
   ```bash
   railway login
   ```

2. Verify secrets are set in GitHub
3. Check Railway dashboard for errors
4. View Railway logs: `railway logs`
5. Manually deploy via Railway dashboard

### Slack notifications not working?

- Verify SLACK_WEBHOOK_URL is set correctly
- Test webhook: 
  ```bash
  curl -X POST -H 'Content-type: application/json' \
    --data '{"text":"Test"}' \
    $SLACK_WEBHOOK_URL
  ```
- Check Slack app permissions

## Best Practices

### Commit Messages
Use conventional commits for clarity:
```bash
git commit -m "feat: add new API endpoint"
git commit -m "fix: resolve authentication bug"
git commit -m "test: add unit tests"
git commit -m "chore: update dependencies"
```

### Branch Protection

Set up branch protection to require CI to pass:
1. Settings → "Branches"
2. Add rule for `main`
3. Require "CI - Lint, Type Check, and Test" to pass
4. Require pull request reviews

### Secrets Management

- Never commit `.env` files
- Use GitHub Secrets for sensitive data
- Rotate Railway token yearly
- Revoke leaked tokens immediately

### Monitoring

Check CI/CD health weekly:
1. View Actions dashboard
2. Review failed workflows
3. Check deployment status
4. Monitor Railway logs

## Advanced Configuration

### Environment-Specific Deployments

```yaml
on:
  push:
    branches: [ main, staging ]

jobs:
  deploy:
    environment:
      name: ${{ github.ref_name }}
```

### Conditional Steps

```yaml
- name: Deploy to production
  if: github.ref == 'refs/heads/main'
  run: railway up
```

### Caching Dependencies

```yaml
- uses: actions/setup-python@v4
  with:
    cache: 'pip'  # Cache pip packages
```

## Documentation Links

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Railway CLI Reference](https://docs.railway.app/reference/cli-api)
- [pytest Documentation](https://docs.pytest.org/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)

## Next Steps

1. ✅ Add workflow files (done)
2. ✅ Configure GitHub Secrets (do now)
3. ✅ Test CI pipeline
4. ✅ Test deployment
5. Optional: Add branch protection rules
6. Optional: Add Slack notifications
7. Optional: Add code coverage requirements

## Summary

Your project now has:
- ✅ Automated testing on every commit
- ✅ Code quality checks
- ✅ Automated deployment on main branch
- ✅ Health checks and notifications
- ✅ Integration with Railway
- ✅ Slack notifications (optional)

Push to `main` and watch your code automatically test and deploy! 🚀
