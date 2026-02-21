# Remaining Tasks (Post–Pre-Submission Work)

Summary of what is **done** in the repo vs what is **left for you** (manual or external).

---

## Done (in this repo)

- **Code:** `validate_search_results()` wired in; Langfuse fallback (`get_prompt_safe`); context length guards; `session_id` in `generate_plan()`; strategic comments; crash-recovery comment in `main.py`; `validate_all_variables` docstring.
- **Docker:** `app/` and `scripts/` in image; `start.sh` for start; backend and React in docker-compose.
- **Langfuse:** Block D prompts pushed via `app/init_langfuse_prompts.py` (run completed); new versions have production label.
- **Docs:** README (Option A UV + Option B venv+pip, etc.); DEPLOYMENT.md; EVALUATION.md; RAILWAY_DEPLOY; TESTING; BEST_PRACTICES; LOCALHOST_TEST_LINKS; CLI_LANGFUSE_RAILWAY; REMAINING_TASKS; transcript (4-task plan, footnote, imperfect reflection). Redundant docs removed (TEST_AND_DOCKER_EXECUTION_REPORT, RAILWAY_* extras, REACT_FRONTEND_SUMMARY).
- **Scripts:** All under `scripts/` (start.sh, update_langfuse_prompts_cli.sh, railway_setup_volume_and_vars.sh, prompts/*.json). Railway and Docker use `bash scripts/start.sh`.
- **Tests:** `make test`, `make lint`, `make react-test` passing; Docker build succeeds.

---

## Remaining (for you to do)

### 1. Langfuse (Block D) — CLI or dashboard

**Option A — CLI (recommended):** From repo root, run:
```bash
bash scripts/update_langfuse_prompts_cli.sh
```
Requires `.env` with `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY`. Creates new versions with Block D text. Then in the Langfuse dashboard, apply the **production** label to the new versions.

**Option B — Dashboard:** Edit the 5 prompts in the Langfuse UI and add the same text; apply **production** label.

Block D content: **generate-plan** — no final compile/synthesize task; **refine-query** — query only, authoritative sources; **compress-results** — preserve article refs (e.g. GDPR Art 5, BDSG §26); **reflect** — one sentence, state gap if not addressed; **generate-report** — Sources section, cite articles explicitly.

See [docs/CLI_LANGFUSE_RAILWAY.md](CLI_LANGFUSE_RAILWAY.md) for full CLI usage.

### 2. Railway (A7) — CLI or dashboard

**Option A — CLI:** From repo root (with `railway login` and project linked):
```bash
bash scripts/railway_setup_volume_and_vars.sh
```
Or manually: `railway volume add --mount-path /app/data`. Optionally: `railway variables --set OPENAI_MODEL=gpt-4o`.

**Option B — Dashboard:** Add a volume at **`/app/data`**; optionally **`/app/reports`** and **OPENAI_MODEL=gpt-4o**.

### 3. Manual / local verification

- **Docker:** Run `docker compose up --build`. Confirm http://localhost:8000/health and http://localhost:8000/docs; if the backend container exits, run without `-d` to see logs and ensure `.env` is present.
- **E2E:** Run a full session (start → plan → execute tasks → report) with real API keys in `.env`.
- **Langfuse fallback:** Temporarily set `LANGFUSE_SECRET_KEY=invalid` and run a session; it should complete using inline prompts.
- **Push:** When satisfied, `git push origin main` (your branch is ahead by several commits).

---

## Quick reference

| Area        | Where        | Action |
|------------|--------------|--------|
| Prompts    | CLI or UI    | `bash scripts/update_langfuse_prompts_cli.sh` then set `production` label in UI |
| Persistence| CLI or UI    | `railway volume add -m /app/data` or Railway dashboard |
| Model      | Railway vars | `railway variables --set OPENAI_MODEL=gpt-4o` (optional) |
| Smoke test | Local/Docker | Health, /docs, full session with API keys |
| Publish    | Git          | `git push origin main` after review |
