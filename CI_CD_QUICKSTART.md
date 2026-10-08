# CI/CD Quick Start - 5 Minutes

Get automated testing and deployment running in 5 minutes.

## What You're Getting

✅ **Auto-test on every commit** - Lint, type check, unit tests
✅ **Auto-deploy on main branch** - Push to Git → Deploy to Railway automatically
✅ **Slack notifications** - Know when deployments succeed/fail
✅ **Health checks** - Verify services are running after deploy

## Step 1: Get Railway Token (2 minutes)

1. Go to https://railway.app/dashboard
2. Click your profile → API Tokens
3. Create new token → Copy full value
4. Save for Step 3

## Step 2: Get Railway Project ID (1 minute)

1. Go to https://railway.app/dashboard
2. Click your project
3. URL: `railway.app/project/{PROJECT_ID}`
4. Copy the PROJECT_ID
5. Save for Step 3

## Step 3: Add GitHub Secrets (2 minutes)

1. Go to your GitHub repo
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"

**Add these 2 secrets:**

```
RAILWAY_TOKEN
<paste token from Step 1>

RAILWAY_PROJECT_ID
<paste project ID from Step 2>
```

Optional (for notifications):
```
RAILWAY_PUBLIC_URL
https://gateway-service-prod.up.railway.app

SLACK_WEBHOOK_URL
https://hooks.slack.com/services/T.../B.../...
```

## Step 4: Test It (automatic)

1. Make a commit and push to `main`:
```bash
git commit --allow-empty -m "test: trigger CI/CD"
git push origin main
```

2. Go to your GitHub repo → "Actions" tab
3. Watch workflows run automatically:
   - **CI workflow** starts (5-10 min)
   - Tests run on all services
   - If CI passes → **Deploy workflow** starts
   - Services deploy to Railway
   - Slack notification sent

## Done! 🎉

Now every time you push to `main`:
1. ✅ Code is automatically tested
2. ✅ Docker images are built
3. ✅ If everything passes → automatically deployed to Railway
4. ✅ You get a Slack notification
5. ✅ Services restart on Railway

## Workflow Status

Check status anytime:
- **GitHub:** Repo → Actions tab
- **Railway:** Dashboard → Deployments
- **Slack:** Check notifications

## Common Commands

```bash
# Push to trigger CI/CD
git commit -m "feat: new feature"
git push origin main

# View workflow logs
# Go to: GitHub → Actions → click workflow

# Manual deployment (if needed)
# Go to: GitHub → Actions → Deploy to Railway → Run workflow

# Check Railway status
# Go to: railway.app → Dashboard
```

## Next Steps

- Review CI/CD_SETUP.md for detailed configuration
- Set up branch protection to require CI to pass
- Add code coverage requirements
- Customize tests and linting rules
- Monitor failed deployments in Actions tab

## Troubleshooting

**Deployment not starting?**
- Verify both secrets are added
- Check Railway project is active
- Look at Actions logs for error

**Tests failing?**
- View CI workflow logs
- Check for database/Redis connection errors
- Run tests locally: `pytest`

**Slack not working?**
- Verify SLACK_WEBHOOK_URL is correct
- Optional - can skip if not needed

---

**Status:** ✅ CI/CD Pipeline Ready

Now you can focus on coding. Tests run automatically. Deployments happen automatically. 🚀
