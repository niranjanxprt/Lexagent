# Railway Frontend Setup

The Streamlit and React services have been added to your Railway project. Complete these steps in the **Railway Dashboard** to deploy them.

**Dashboard**: https://railway.com/project/b7165aa2-b31f-4a95-8194-51029e0758b2

## 1. Streamlit Service

1. Open [Railway Dashboard](https://railway.com/dashboard) → **lexagent** project
2. Click the **streamlit** service
3. Go to **Settings**
4. Under **Build**:
   - **Root Directory**: leave empty (uses repo root)
   - **Config Path**: `/railway-streamlit.toml`
5. Under **Variables**, add:
   - `LEXAGENT_API_URL` = `https://lexagent-production.up.railway.app`
6. Go to **Deployments** → **Redeploy** (or push to GitHub to trigger deploy)
7. Go to **Settings** → **Networking** → **Generate Domain**

## 2. React Service

1. Open the **react** service
2. Go to **Settings**
3. Under **Build**:
   - **Root Directory**: `frontend-react`
   - Config is auto-detected from `frontend-react/railway.toml`
4. Under **Variables**, add (required for build):
   - `VITE_API_URL` = `https://lexagent-production.up.railway.app`
5. Redeploy
6. **Settings** → **Networking** → **Generate Domain**

## 3. Connect GitHub (if not already)

- Project → **Settings** → **Connect Repo** → select your Lexagent repo
- Each service will deploy from the repo. Set watch paths if needed:
  - Streamlit: `frontend/**`, `app/**`, `requirements.txt`
  - React: `frontend-react/**`

## After Setup

Once domains are generated, you'll have:
- **Backend API**: https://lexagent-production.up.railway.app
- **Streamlit**: https://streamlit-production.up.railway.app (or similar)
- **React**: https://react-production.up.railway.app (or similar)
