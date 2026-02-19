# Connect Lexagent Service to GitHub (Required for Deploy)

The Lexagent service has no deployments because it has no **source** configured. Connect the GitHub repo so Railway can build and deploy.

## Steps (Dashboard)

1. Open [Railway Dashboard](https://railway.app/dashboard) → **lexagent** project
2. Click the **Lexagent** service
3. Go to **Settings** → **Source** (or **Service Source**)
4. Click **Connect Repo** (or **Change Source**)
5. Select **GitHub** and choose `niranjanxprt/Lexagent`
6. Select branch: `main`
7. Save

Railway will trigger a build from the repo. Ensure:
- **Root Directory**: empty
- **Config Path**: `/railway.toml`
- **Builder**: Dockerfile (from railway.toml)

## After First Deploy

1. **Settings** → **Networking** → **Generate Domain**
2. Set variable `VITE_API_URL` = `https://<your-domain>.railway.app`
3. Redeploy so React uses the correct API URL

## Variables

Add in **Settings** → **Variables**:
- `OPENAI_API_KEY`
- `TAVILY_API_KEY`
- `LANGFUSE_SECRET_KEY`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_BASE_URL` (optional)
