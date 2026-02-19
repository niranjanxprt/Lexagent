# Railway: Railpack vs Dockerfile

Railpack is Railway’s zero-config builder that auto-detects languages and builds images. It can replace the Dockerfile for Lexagent if configured correctly.

## Would Railpack solve the deployment issues?

**Yes.** Railpack can build both Python (FastAPI) and React (Vite) in one service, similar to the current Dockerfile. The main requirement is making Node available during the build and wiring the build/start commands correctly.

## Trade-offs

| Aspect | Dockerfile | Railpack |
|--------|------------|----------|
| **Control** | Full control over stages and layers | Config-driven, less low-level control |
| **Detection** | None – explicit instructions | Auto-detects Python at root |
| **Multi-language** | Straightforward (multi-stage) | Needs `RAILPACK_PACKAGES` + build command |
| **Railway priority** | Used if `Dockerfile` exists at root | Used only when no root `Dockerfile` |
| **Build time** | Often faster (BuildKit caching) | Similar with Railpack’s caching |

## How to use Railpack for Lexagent

Railway prefers a root `Dockerfile` over Railpack. To use Railpack, either:

1. **Rename the Dockerfile** (e.g. `Dockerfile.railway`), or  
2. **Remove the root Dockerfile** and rely on Railpack.

Then configure Railpack for Python + Node.

### 1. Environment variables (Railway Dashboard or CLI)

```bash
# Node must be available during build
RAILPACK_PACKAGES="node@22"

# Start command (FastAPI uses app.main:app, not main:app)
RAILPACK_START_CMD="uvicorn app.main:app --host 0.0.0.0 --port $PORT"

# Build: install Python deps, build React, copy dist → static
RAILPACK_BUILD_CMD="pip install -r requirements.txt && cd frontend-react && npm install && npm run build && cd .. && mkdir -p static && cp -r frontend-react/dist/* static/"
```

### 2. `VITE_API_URL` at build time

Set `VITE_API_URL` in Railway variables to your backend domain (e.g. `https://lexagent-production.up.railway.app`). Vite reads it at build time for API calls.

### 3. `railway.toml` (optional overrides)

```toml
[build]
builder = "RAILPACK"
# No dockerfilePath when using Railpack

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 10
```

### 4. `railpack.json` (optional, for more control)

```json
{
  "$schema": "https://schema.railpack.com",
  "packages": {
    "python": "3.11",
    "node": "22"
  },
  "deploy": {
    "base": { "image": "ghcr.io/railwayapp/railpack-runtime:latest" }
  }
}
```

Environment variables above are usually enough; this file is for advanced tuning.

## Recommendation

- **If the Dockerfile build is working:** keep using it. It’s explicit and already set up.
- **If you want to try Railpack:** rename `Dockerfile` → `Dockerfile.backup`, set `RAILPACK_PACKAGES`, `RAILPACK_BUILD_CMD`, `RAILPACK_START_CMD`, and `VITE_API_URL`, then redeploy.

Railpack is a valid alternative and can resolve the same deployment issues as the Dockerfile when configured correctly.
