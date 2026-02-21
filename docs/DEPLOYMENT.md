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
| `OPENAI_MODEL` | Optional | Default `gpt-4o-mini`; use `gpt-4o` for stronger legal reasoning |
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

### Deploy

- **CLI:** `railway up` (from project root; uses `railway.toml` and Dockerfile).
- **Git:** Connect the repo in Railway; pushes to the linked branch trigger a build. Build uses the same Dockerfile.

### Health check

Railway uses the `/health` endpoint:

```http
GET /health → {"status": "ok"}
```

Configure in Railway: **Settings → Health Check** with path `/health` if needed.

---

## Local Docker (API + React)

The backend image builds React and serves it at `/`. One container = full app.

```bash
docker compose up --build backend
```

- **http://localhost:8000** — React UI + API (same as Railway)

Or `docker compose up --build` to also run a separate React container on :3000; the backend alone is enough for testing.

Volumes in `docker-compose.yml`:

- `./data:/app/data` — session JSON
- `./reports:/app/reports` — report markdown

Data persists across container restarts. Same behavior as running `make backend` and `make react` locally.

### Session data and git

**Sessions and reports are not in git.** They are in `.gitignore` (`data/*.json`, `reports/*.md`). When you clone the repo or redeploy:

- **Local:** You get empty `data/` and `reports/` (or `.gitkeep` only). Sessions persist only if you keep the same `./data` and `./reports` directories between runs.
- **Docker:** Volumes `./data:/app/data` and `./reports:/app/reports` persist data across `docker compose` restarts. A fresh clone has no prior sessions.
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
