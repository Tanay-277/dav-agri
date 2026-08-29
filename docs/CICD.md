# CI/CD Setup

## Overview

This project uses GitHub Actions for continuous integration and deployment:

- **Frontend**: Deployed to **Vercel** on every push to `main`
- **Backend**: Deployed to **Railway** on every push to `main`
- **PR Checks**: Lint, typecheck, build, and tests run on every PR to `main`

## Authorization & Security

### 1. Branch Protection Rules

Go to **Settings → Branches → Branch protection rules** and add a rule for `main`:

| Setting | Value |
|---------|-------|
| Require a pull request before merging | ✅ |
| Require approvals | 1 |
| Require status checks to pass before merging | ✅ |
| Required status checks | `frontend-check`, `backend-check` |
| Require branches to be up to date | ✅ |
| Do not allow bypassing settings | ✅ |

### 2. Required GitHub Secrets

Add these secrets in **Settings → Secrets and variables → Actions**:

#### Frontend (Vercel)
| Secret | Description | How to get |
|--------|-------------|------------|
| `VERCEL_TOKEN` | Vercel API token | Run `vercel login`, then `vercel tokens add` |
| `VERCEL_ORG_ID` | Vercel Organization ID | Run `vercel link` in frontend directory, check `.vercel/project.json` |
| `VERCEL_PROJECT_ID` | Vercel Project ID | Same as above, check `.vercel/project.json` |

#### Backend (Railway)
| Secret | Description | How to get |
|--------|-------------|------------|
| `RAILWAY_TOKEN` | Railway API token | Run `railway login`, then check `~/.railway/token.json` |
| `RAILWAY_PROJECT_ID` | Railway Project ID | Run `railway status` in backend directory |
| `RAILWAY_SERVICE_ID` | Railway Service ID | Run `railway status` in backend directory |

## Workflows

### Deploy Workflow (`.github/workflows/deploy.yml`)

Triggers:
- Push to `main` branch
- Manual `workflow_dispatch`

Jobs:
1. `authorize` - Validates deployment authorization (blocks Dependabot)
2. `frontend-deploy` - Builds and deploys frontend to Vercel
3. `backend-deploy` - Runs tests and deploys backend to Railway

### PR Check Workflow (`.github/workflows/pr-check.yml`)

Triggers on every PR to `main`.

Jobs:
1. `frontend-check` - Lint, typecheck, and build frontend
2. `backend-check` - Install deps and run backend tests

## Railway Environment Variables

Configure these in the Railway dashboard or via `railway variables set`:

| Variable | Description | Example |
|----------|-------------|---------|
| `CORS_ORIGINS` | Allowed frontend origins (comma-separated) | `https://your-app.vercel.app,http://localhost:5173` |
| `DATASET_FILE` | CSV dataset filename | `agriculture.csv` |
| `DEBUG` | Debug mode | `false` |
| `GEMINI_API_KEY` | Optional Gemini AI key | (leave empty if unused) |

**Note**: `HOST`, `PORT`, and `DATASET_FILE` have safe defaults in `backend/core/config.py`. `GEMINI_API_KEY` defaults to empty string. Only `CORS_ORIGINS` must be explicitly set to your production frontend URL.

## Railway Deployment Configuration

The file `backend/railway.toml` configures Railway deployment:

- **Builder**: Nixpacks (auto-detects Python)
- **Start command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Health check**: `/api/health`
- **Restart policy**: Restart on failure, max 10 retries

## Local Deployment

### Frontend
```bash
cd frontend
vercel login
vercel link
vercel --prod
```

### Backend
```bash
cd backend
railway login
railway link
railway up
```

## Environment Protection

The deploy workflow uses GitHub Environments:
- `production` environment is configured with required reviewers
- Only authorized users can approve production deployments
- Secrets are scoped to the environment for additional security

## Rollback

### Vercel
- Use `vercel rollback [deployment-url]` or rollback via Vercel Dashboard

### Railway
- Use `railway rollback` or redeploy a previous deployment via Railway Dashboard
- Railway retains deployment history automatically

## Notes on Railway Native Integration

Railway offers native GitHub integration for automatic deployments. If you enable Railway's native GitHub integration, it will deploy on push to `main`. This would duplicate the `backend-deploy` job in our GitHub Actions workflow. Choose one approach:

1. **GitHub Actions (current setup)**: Full control over build, test, and deployment pipeline
2. **Railway Native Integration**: Simpler setup but less control over CI gates

Do not enable both simultaneously to avoid duplicate deployments.
