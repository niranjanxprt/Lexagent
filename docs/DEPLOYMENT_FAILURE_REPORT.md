# Deployment Failure Report

**Date:** 2026-02-21  
**Context:** Demo failed; Railway deployments failing.

---

## What Was Checked

1. **Local Docker build** — Succeeds. Image builds with `scripts/start.sh`, `COPY scripts/`, and `chmod +x scripts/start.sh`.
2. **Local container run** — Running `bash scripts/start.sh` inside the built image starts uvicorn and `/health` returns 200.
3. **Railway** — Project is linked (`railway status` OK). Logs were not fully captured in this session (CLI may stream/hang).
4. **Git history** — Before the “scripts under scripts/” change, the app used **`start.sh` in the repo root** and `startCommand = "bash start.sh"`.

---

## Likely Cause

The change that **moved `start.sh` to `scripts/`** and set `startCommand = "bash scripts/start.sh"` can break Railway if:

- **Build context differs** (e.g. deploy from GitHub and `scripts/` is excluded or not present in the same way).
- **Working directory at runtime** is not `/app`, so `scripts/start.sh` is not found.
- **Caching** — an old build or deploy step is reused and expects `start.sh` at root.

Reverting only the **startup path** (start.sh back to root, `startCommand = "bash start.sh"`) removes this variable while keeping all other changes (prompts, docs, other scripts in `scripts/`).

---

## Rollback Applied (Deployment Only)

- **`start.sh`** restored in the **repo root** (same content as `scripts/start.sh`).
- **Dockerfile** — Copies `start.sh` at root again; no longer copies `scripts/` for startup (still copies `scripts/` if needed for other tooling; we can remove that copy if you want a minimal image).
- **railway.toml** — `startCommand = "bash start.sh"`.
- **Docs** — RAILWAY_DEPLOY.md and DEPLOYMENT.md updated to say `start.sh` at root.

No application code, prompts, or doc cleanup was reverted. The rest of `scripts/` (e.g. `update_langfuse_prompts_cli.sh`, `railway_setup_volume_and_vars.sh`) remains and is for local/CLI use only.

---

## What You Should Do

1. **Commit the rollback** (this report + the file changes).
2. **Redeploy:** `railway up` or push to the branch Railway watches.
3. **Confirm:** Hit your Railway URL `/health` and run a short flow (e.g. start session, one task).
4. If it still fails, **share the latest Railway build and runtime logs** (from the Railway dashboard or `railway logs`) so we can target the next fix.

---

## If You Want a Full Rollback

To revert to the state before all pre-submission changes (e.g. commit before `0d396c2`):

```bash
git log --oneline  # pick the commit before 0d396c2
git revert --no-commit <range>  # or git reset --hard <commit>
```

Only do this if you want to discard prompt/docs/script changes and need the last known-good deploy ASAP.
