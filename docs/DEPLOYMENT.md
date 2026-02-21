# Deployment Guide

## Current: Railway (Docker)

LexAgent is deployed as a single container: the Dockerfile builds the React frontend and the Python backend serves both the API and the React app. Streamlit is **not** run on Railway; use the React UI or run Streamlit locally against the deployed API.

### How the Docker build works

- **Stage 1 (frontend):** Node builds `frontend-react` with `npm run build:docker`; output is copied to `./static`.
- **Stage 2 (runtime):** Python 3.11 image; `app/`, `frontend/`, `static/`, and `start.sh` are copied. `start.sh` runs `uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`.

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

### Persistent storage on Railway

Sessions and reports are written to `/app/data` and `/app/reports`. Without a volume, they are ephemeral (lost on redeploy). To persist:

1. Railway Dashboard → your service → Volumes
2. Add a volume and set **Mount Path** to `/app/data`
3. Optionally add a second volume for `/app/reports`

The app does not create these directories on a read-only filesystem; the volume mount provides a writable path.

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

## Local Docker (API + React, optional Streamlit)

```bash
# Backend only (API + React at http://localhost:8000)
docker compose up --build backend

# Backend + Streamlit (Streamlit at http://localhost:8501, talks to backend)
docker compose up --build
```

Volumes in `docker-compose.yml`:

- `./data:/app/data` — session JSON
- `./reports:/app/reports` — report markdown

So data persists across container restarts. Same behavior as running `make backend` and `make frontend` locally with the same env.

---

## Local run (no Docker)

```bash
uv sync
cp .env.example .env   # add OPENAI_API_KEY, TAVILY_API_KEY
uv run python app/init_langfuse_prompts.py   # if using Langfuse

# Terminal 1
make backend    # http://localhost:8000

# Terminal 2 — pick one
make frontend  # Streamlit http://localhost:8501
make react     # React dev server http://localhost:5173
```

Or `make dev` to start backend and Streamlit in the background (see Makefile).

**Local testing URLs:** With the backend running, use **http://localhost:8000/health** (`{"status":"ok"}`), **http://localhost:8000/docs** (Swagger), **http://localhost:8000/sessions** (list sessions). With Streamlit: **http://localhost:8501**. With React dev: **http://localhost:5173**. Smoke test: `curl http://localhost:8000/health`.

---

## What to add for production

1. **Auth:** JWT or API keys on `/agent/*`; rate limiting per user.
2. **CORS:** Restrict `allow_origins` to your frontend domain(s).
3. **Logging:** Structured logs (e.g. structlog) and log aggregation.
4. **Database:** Replace JSON in `storage.py` with Postgres/SQLite for concurrency and scale.
5. **Secrets:** Use a secret manager (e.g. Railway variables, Vault); avoid committing keys.
6. **CI/CD:** Lint and tests on push; deploy on merge to main.
