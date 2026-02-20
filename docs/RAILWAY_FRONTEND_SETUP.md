# Railway Frontend Setup

The React frontend is served by the same service as the FastAPI backend. Deployment uses the main **Dockerfile** (multi-stage build: React + FastAPI).

**Dashboard**: https://railway.com/project/b7165aa2-b31f-4a95-8194-51029e0758b2

## Deployment

1. Open [Railway Dashboard](https://railway.com/dashboard) → **lexagent** project
2. The service builds from the repo root using the main **Dockerfile** (no separate Streamlit or React service config)
3. Under **Variables**, add as needed:
   - `VITE_API_URL` — used at build time for the React frontend (e.g. `https://lexagent-production.up.railway.app`)
   - API keys and other backend env vars
4. Push to `main` to trigger deploy. The Dockerfile builds the React app and runs FastAPI; the app serves the React static files and the API at the same origin.

## Connect GitHub (if not already)

- Project → **Settings** → **Connect Repo** → select your Lexagent repo
- Deployments run from the repo; the Dockerfile builds the React bundle and starts the backend.

## After Setup

Once the domain is generated you have:
- **Backend API + React app**: https://lexagent-production.up.railway.app (or your generated domain)
