# Deployment Guide

## Current: Railway (Docker)

LexAgent is deployed as a single container: the Dockerfile builds the React frontend and the Python backend serves both the API and the React app.

### How the Docker build works

- **Stage 1 (frontend):** Node builds `frontend-react` with `npm run build:docker`; output is copied to `./static`.
- **Stage 2 (runtime):** Python 3.11 image; `app/`, `static/`, and `start.sh` are copied. `start.sh` runs `uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`.

Served paths:

- `/` — React app (from `/app/static`)
- `/docs` — FastAPI Swagger UI
- `/agent/*` — API endpoints

### Railway environment variables

| Variable | Required | Notes |
|----------|----------|--------|
| `OPENAI_API_KEY` | Yes | |
| `TAVILY_API_KEY` | Yes | |
| `LANGFUSE_SECRET_KEY` | Recommended | Agent falls back to inline prompts if missing/unreachable |
| `LANGFUSE_PUBLIC_KEY` | Recommended | |
| `LANGFUSE_BASE_URL` | Optional | Defaults to Langfuse cloud |
| `OPENAI_MODEL` | Optional | Default `gpt-4.1-mini`; plan/report use full `gpt-4.1` automatically |
| `PORT` | Set by Railway | Do not override |
| `LEXAGENT_DATA_DIR` | Optional | Session path (default `/app/data`). Use if volume is elsewhere (e.g. `/app/persist/data`) |
| `LEXAGENT_REPORTS_DIR` | Optional | Report path (default `/app/reports`). Use if volume is elsewhere (e.g. `/app/persist/reports`) |

### Persistent storage on Railway

Sessions and reports are written to disk (not memory). Without a volume, they are ephemeral and lost on redeploy.

**Option A — Default paths:** Add volumes at `/app/data` and optionally `/app/reports`:
1. Railway Dashboard → your service → Volumes
2. Add volume → **Mount Path** `/app/data`
3. Optionally add a second volume at `/app/reports`

**Option B — Volume at `/app/persist`:** Set Railway variables:
- `LEXAGENT_DATA_DIR=/app/persist/data`
- `LEXAGENT_REPORTS_DIR=/app/persist/reports`

The app creates these directories on first write. The volume mount provides a writable path.

### Pre-merge verification (dev → main)

Before merging dev to main, run:

```bash
bash scripts/verify_before_merge.sh
```

This runs tests, lint, Docker build, and endpoint checks. Railway uses the same Dockerfile; no Streamlit—backend serves React at `/` and API at `/agent/*`.

### Railway step-by-step (first time)

1. **Init:** `railway init` (create or link project); `railway login`.
2. **Variables:** `railway variables --set "OPENAI_API_KEY=..."` and `TAVILY_API_KEY`; add `LANGFUSE_SECRET_KEY`, `LANGFUSE_PUBLIC_KEY` (and optionally `LANGFUSE_BASE_URL`, `OPENAI_MODEL=gpt-4.1-mini`).
3. **Deploy:** `railway up` (uses `railway.toml` and Dockerfile).
4. **Domain:** `railway domain` or Dashboard → Settings → Networking → Generate Domain.
5. **Volumes:** `railway volume add --mount-path /app/data` (and optionally `/app/reports`). Or Dashboard → Volumes → Add volume.

Connecting GitHub to Railway triggers deploys on push; variables and volumes are unchanged.

### CLI quick reference

| Goal | Command |
|------|---------|
| Update all Langfuse prompts | `bash scripts/update_langfuse_prompts_cli.sh` |
| Add Railway volume `/app/data` | `railway volume add --mount-path /app/data` |
| Set Railway model | `railway variables --set OPENAI_MODEL=gpt-4.1-mini` |
| List Langfuse prompts | `npx langfuse-cli --env .env api prompts list` |
| List Langfuse datasets | `npx langfuse-cli --env .env api datasets list` |
| List Railway volumes | `railway volume list` |
| List Railway variables | `railway variables` |

### Deploy (ongoing)

- **CLI:** `railway up` (from project root).
- **Git:** Pushes to the linked branch trigger a build.

### Health check

Railway uses the `/health` endpoint:

```http
GET /health → {"status": "ok"}
```

Configure in Railway: **Settings → Health Check** with path `/health` if needed.

---

## Test Docker image locally (optional)

Same image as Railway. Requires `.env` with `OPENAI_API_KEY` and `TAVILY_API_KEY`.

```bash
docker build -t lexagent .
docker run -p 8000:8000 --env-file .env -v "$(pwd)/data:/app/data" -v "$(pwd)/reports:/app/reports" lexagent
```

- **http://localhost:8000** — React UI + API (same as Railway)

### Session data and git

**Sessions and reports are not in git.** They are in `.gitignore` (`data/*.json`, `reports/*.md`). When you clone the repo or redeploy:

- **Local:** You get empty `data/` and `reports/` (or `.gitkeep` only). Sessions persist only if you keep the same `./data` and `./reports` directories between runs.
- **Docker:** Use `-v` to mount `./data` and `./reports`; data persists across container restarts. A fresh clone has no prior sessions.
- **Railway:** Sessions persist only if you have a volume mounted at `/app/data` (or `LEXAGENT_DATA_DIR`). Without a volume, each redeploy starts with no sessions.

The React frontend stores the last-viewed session ID in browser `localStorage`; that is per-browser and not in git.

---

## Local run (no Docker)

```bash
uv sync
cp .env.example .env   # add OPENAI_API_KEY, TAVILY_API_KEY
uv run python app/init_langfuse_prompts.py   # if using Langfuse

# Terminal 1
make backend    # http://localhost:8000

# Terminal 2
make react     # React dev server http://localhost:5173
```

Or `make dev` to start backend and React together (see Makefile).

**Local testing URLs:** With the backend running, use **http://localhost:8000/health** (`{"status":"ok"}`), **http://localhost:8000/docs** (Swagger), **http://localhost:8000/sessions** (list sessions). With React dev: **http://localhost:5173**. Smoke test: `curl http://localhost:8000/health`.

---

## What to add for production

1. **Auth:** JWT or API keys on `/agent/*`; rate limiting per user.
2. **CORS:** Restrict `allow_origins` to your frontend domain(s).
3. **Logging:** Structured logs (e.g. structlog) and log aggregation.
4. **Database:** Replace JSON in `storage.py` with Postgres/SQLite for concurrency and scale.
5. **Secrets:** Use a secret manager (e.g. Railway variables, Vault); avoid committing keys.
6. **CI/CD:** Lint and tests on push; deploy on merge to main.
