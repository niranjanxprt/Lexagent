# Railway Deployment — Backend + React Only

Single-service deployment: the **lexagent** backend serves both the API and React UI.

## Prerequisites

- Railway CLI: `npm i -g @railway/cli` or `brew install railway`
- Logged in: `railway login`

## Deploy

```bash
railway service lexagent
railway up
```

## Required Variables (set in Dashboard or via CLI)

```bash
railway variables --set "OPENAI_API_KEY=sk-..."
railway variables --set "TAVILY_API_KEY=tvly-..."
railway variables --set "LANGFUSE_SECRET_KEY=sk-lf-..."
railway variables --set "LANGFUSE_PUBLIC_KEY=pk-lf-..."
railway variables --set "LANGFUSE_BASE_URL=https://cloud.langfuse.com"
railway variables --set "VITE_API_URL=https://YOUR-BACKEND-DOMAIN.railway.app"
```

`VITE_API_URL` is used at build time for the React app. Set it to your backend domain (e.g. `https://lexagent-production.up.railway.app`).

## Dashboard Settings (if build fails)

**Critical:** The lexagent service must use Dockerfile, not Nixpacks. See [RAILWAY_FIX_BUILDER.md](RAILWAY_FIX_BUILDER.md) for full steps.

1. Go to Railway Dashboard → lexagent project → **lexagent** service
2. **Settings** → **Build** (or Source):
   - **Builder**: set to **Dockerfile** (not Nixpacks)
   - **Dockerfile Path**: `Dockerfile`
   - **Root Directory**: empty
   - **Config Path**: `/railway.toml` or empty
3. Redeploy

## Verify

- **URL**: https://lexagent-production.up.railway.app
- **API**: https://lexagent-production.up.railway.app/health → `{"status":"ok"}`
- **React UI**: https://lexagent-production.up.railway.app/ → should load the React app

If `/` returns 404, the build likely used Nixpacks (Python only) instead of the Dockerfile (Python + React). Check build logs and fix the builder as above.
