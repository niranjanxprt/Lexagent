# Railway Deployment (CLI Only)

Deploy LexAgent backend to Railway using only the Railway CLI. No MCP servers.

## Prerequisites

1. **Railway account**: [railway.app](https://railway.app)
2. **Railway CLI installed**:
   ```bash
   npm i -g @railway/cli
   # or: brew install railway
   ```
3. **Login**:
   ```bash
   railway login
   ```

## Pre-Deploy: Add Railway Config

Create these files in the project root before deploying.

### Option A: `railway.toml`

```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 10
```

### Option B: `Procfile`

```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Python version (optional)

Create `.python-version` in project root:

```
3.11
```

Railway/Nixpacks will use this. The project has `requirements.txt`; Nixpacks will run `pip install -r requirements.txt`.

## Deployment Steps

### 1. Initialize project (first time only)

```bash
cd /path/to/Lexagent
railway init
```

Follow prompts to create a new project or link to an existing one.

### 2. Set environment variables

```bash
railway variables --set "OPENAI_API_KEY=sk-your-key"
railway variables --set "TAVILY_API_KEY=tvly-your-key"
```

Langfuse (required for prompts/tracing):

```bash
railway variables --set "LANGFUSE_SECRET_KEY=sk-lf-..."
railway variables --set "LANGFUSE_PUBLIC_KEY=pk-lf-..."
railway variables --set "LANGFUSE_BASE_URL=https://cloud.langfuse.com"
```

Optional (model):

```bash
railway variables --set "OPENAI_MODEL=gpt-4o-mini"
```

### 3. Deploy

```bash
railway up
```

This uploads the project and triggers a build. Wait for the build to complete.

### 4. Generate public domain

```bash
railway domain
```

Or: Railway Dashboard → your service → Settings → Networking → Generate Domain.

### 5. Verify

```bash
curl https://your-app.railway.app/health
```

Expected: `{"status":"ok"}`

Test agent start:

```bash
curl -X POST https://your-app.railway.app/agent/start \
  -H "Content-Type: application/json" \
  -d '{"goal":"Research EU AI Act Article 3"}'
```

## Connecting GitHub

Connecting your GitHub repo **will not break** the existing deployment. Railway supports both:
- **CLI deploys** (`railway up`) — upload from local
- **GitHub deploys** — auto-deploy on push

When you connect GitHub: Railway will use the repo as the source. Future pushes will trigger new deploys. Your current service, domain, and variables stay the same. You can use both: push to GitHub for CI/CD, or run `railway up` for manual deploys.

To connect: Railway Dashboard → Project → New → GitHub Repo → select your repo.

## Notes

- **Storage**: `data/` and `reports/` are ephemeral. Sessions reset on redeploy. For persistence, add a database later.
- **Langfuse prompts**: Run `uv run python app/init_langfuse_prompts.py` locally with `LANGFUSE_*` set; prompts live in Langfuse, not in the deploy.
- **Frontend**: Deploy backend first. For React, build with `VITE_API_URL=https://your-app.railway.app` and deploy as a separate static service or serve from FastAPI.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Build fails | Ensure `requirements.txt` exists; run `uv pip compile pyproject.toml -o requirements.txt` if needed |
| Port binding | Start command must use `$PORT` and `--host 0.0.0.0` |
| 502 Bad Gateway | Check logs: `railway logs` |
| Missing env vars | `railway variables` to list; set via `railway variables --set "KEY=value"` |
