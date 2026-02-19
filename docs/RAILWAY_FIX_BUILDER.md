# Fix Railway Build: Use Dockerfile Instead of Nixpacks

## Problem

The lexagent service builds with **Nixpacks** (Python only) instead of the **Dockerfile** (Python + React). Result:
- `/health` works (API is fine)
- `/` returns 404 (no React static files)

Build logs show: `using build driver nixpacks-v1.41.0` instead of our Dockerfile.

## How Config-as-Code Works

Per [Railway config-as-code docs](https://docs.railway.com/config-as-code):

> **Configuration defined in code will always override values from the dashboard.**

So our `railway.toml` (with `builder = "DOCKERFILE"`) should override the dashboard — but only if Railway is actually reading it. If the **Config Path** for the lexagent service points to the wrong file (or nowhere), our config is ignored.

## Fix: Set Config Path in Dashboard

1. Open [Railway Dashboard](https://railway.app/dashboard) → **lexagent** project
2. Click the **lexagent** service (domain: `lexagent-production.up.railway.app`)
3. Go to **Settings** → **Source** (or **Build**)
4. Find **Config Path** (or "Config file path")
5. Set it to **`/railway.toml`** (absolute path from repo root)
6. Ensure **Root Directory** is empty (so the repo root is used)
7. Save and **Redeploy** (or push to GitHub)

Once the Config Path points to our `railway.toml`, Railway will read it and use `builder = "DOCKERFILE"` from the file, overriding any dashboard setting.

## Verify

After redeploy, build logs should show:
- `FROM node:20-alpine` and `FROM python:3.11-slim` (not `nixpacks:ubuntu`)

Then:
- https://lexagent-production.up.railway.app/ → React UI
- https://lexagent-production.up.railway.app/health → `{"status":"ok"}`

## If Config Path Is Not Visible

- Look under **Settings** → **Source** or **Build**
- The field may be labeled "Config file", "Config path", or "railway.toml path"
- Use the absolute path: `/railway.toml` (leading slash = from repo root)
