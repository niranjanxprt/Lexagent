# Localhost test links

Use these URLs when the backend is running **locally**.

**Start the backend with either:**
- **UV:** `make backend` or `uv run uvicorn app.main:app --port 8000`
- **venv + pip:** activate your venv, then `uvicorn app.main:app --reload --port 8000` (see README Option B)

## Backend (API + React)

| URL | Description |
|-----|-------------|
| **http://localhost:8000/** | React app only when `static/` exists (e.g. after Docker build). For local run without Docker, use Streamlit at :8501 or React dev at :5173. |
| **http://localhost:8000/docs** | Swagger UI — interactive API docs. |
| **http://localhost:8000/health** | Health check — returns `{"status":"ok"}`. |
| **http://localhost:8000/sessions** | List sessions (GET). |

## With Streamlit (separate process)

1. Start backend: `make backend` (or already running).
2. In another terminal: `make frontend`.
3. Open **http://localhost:8501** — Streamlit UI; set `LEXAGENT_API_URL=http://localhost:8000` in `.env` so it talks to the backend.

## With React dev server (separate process)

1. Start backend: `make backend`.
2. In another terminal: `make react`.
3. Open **http://localhost:5173** — Vite dev server; uses `LEXAGENT_API_URL` from `.env` (default `http://localhost:8000`).

## Docker

- **Backend only:** `docker compose up --build backend`  
  - **http://localhost:8000** — API + React  
  - **http://localhost:8000/docs** — Swagger  
- **Backend + Streamlit:** `docker compose up --build` (ensure port 8501 is free)  
  - **http://localhost:8000** — API + React  
  - **http://localhost:8501** — Streamlit  

If the backend container exits immediately, run `docker compose up backend` (without `-d`) to see logs, and ensure `.env` exists with at least `OPENAI_API_KEY` and `TAVILY_API_KEY`.

## Quick smoke test

1. **Health:** `curl http://localhost:8000/health` → `{"status":"ok"}`  
2. **Docs:** Open http://localhost:8000/docs in a browser.  
3. **Start session:** POST to `/agent/start` with `{"goal": "What does GDPR Article 5 say?"}` (requires API keys in env).
