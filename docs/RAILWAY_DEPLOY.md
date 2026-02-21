# Railway Deployment

Deploy LexAgent to Railway using the **Dockerfile** (recommended). The repo’s `railway.toml` is already set for Docker builds.

## Prerequisites

1. **Railway account**: [railway.app](https://railway.app)
2. **Railway CLI** (optional): `npm i -g @railway/cli` or `brew install railway`
3. **Login**: `railway login`

## Build and run (current setup)

The project uses a **Dockerfile** that:

- Builds the React frontend and copies it into the image as `/app/static`
- Installs Python dependencies from `requirements.txt`
- Runs `start.sh`, which starts: `uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`

`railway.toml` in the repo:

```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"

[deploy]
startCommand = "bash start.sh"
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 10
```

Do **not** switch to Nixpacks or Procfile unless you intend to maintain a separate non-Docker path; the app expects the React build to be present at `/app/static`.

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

## Persistent storage (volumes)

The app writes sessions to `/app/data` and reports to `/app/reports`. Without a volume, these are ephemeral and reset on redeploy.

To persist sessions (and optionally reports):

1. Railway Dashboard → your service → **Volumes**
2. Add a volume with **Mount Path** `/app/data`
3. Optionally add a second volume for **Mount Path** `/app/reports`

The app creates these directories on startup when the mount is writable.

## Notes

- **Langfuse:** Run `uv run python app/init_langfuse_prompts.py` locally once with `LANGFUSE_*` set; prompts live in Langfuse. If Langfuse is unreachable at runtime, the agent uses inline fallback prompts.
- **Frontend:** The same container serves the React app at `/` and the API at `/agent/*` and `/docs`. No separate frontend deploy needed.
- **Streamlit:** Not run on Railway. Use the React UI, or run Streamlit locally with `LEXAGENT_API_URL=https://your-app.railway.app`.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Build fails | Ensure `requirements.txt` exists; run `uv pip compile pyproject.toml -o requirements.txt` if needed |
| Port binding | Start command must use `$PORT` and `--host 0.0.0.0` |
| 502 Bad Gateway | Check logs: `railway logs` |
| Missing env vars | `railway variables` to list; set via `railway variables --set "KEY=value"` |
