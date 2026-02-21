# Remaining Tasks

Summary of what is **done** vs what is **left for you** (manual or external).

---

## Done (in this repo)

- **Code:** V4 prompts; Pydantic ResearchPlan, ReflectResult, Task.reflect_status; model split (gpt-4.1 for plan/report, gpt-4.1-mini for refine/compress/reflect); report includes all source URLs and flags partially-addressed tasks; compress empty-results guard; Langfuse fallback; context length guards; security validation. PROMPT_FALLBACKS and `scripts/prompts/*.json` are synced with `app/init_langfuse_prompts.py`. Observability: `@observe` on search_web, reflect_status/reflect_gap in Langfuse metadata. Tavily retry with exponential backoff in `app/tools.py`. Eval: `scripts/create_eval_dataset.py`, `scripts/run_eval.py` (reflect correctness + Langfuse scoring).
- **Docker:** `app/` and `start.sh` in image; backend and React in docker-compose.
- **Langfuse:** Prompts defined in `app/init_langfuse_prompts.py`; run `bash scripts/update_langfuse_prompts_cli.sh` to push new versions (they get the **production** label automatically). **Prompt sync completed:** code and Langfuse Prompt Management are in sync (all 5 prompts pushed with production label). Re-run the script after any change to `init_langfuse_prompts.py`. You can also edit prompts in the Langfuse UI — changes take effect without redeploy (see [LANGFUSE_SETUP.md](LANGFUSE_SETUP.md)).
- **Docs:** README; DEPLOYMENT (includes Railway step-by-step); EVALUATION; TESTING; LANGFUSE_SETUP; CLI_LANGFUSE_RAILWAY; LEGAL_RESEARCH_PROMPTS_V4; SECURITY; BEST_PRACTICES; transcript. Redundant RAILWAY_DEPLOY merged into DEPLOYMENT.
- **Scripts:** `scripts/update_langfuse_prompts_cli.sh`, `scripts/railway_setup_volume_and_vars.sh`, `start.sh`. Railway/Docker use `bash start.sh`.
- **Tests:** `make test`, `make lint`, `make react-test` passing; Docker build succeeds.

---

## Remaining (for you to do)

### 1. Langfuse — keep in sync or edit in UI

**Status:** Code and Langfuse Prompt Management are currently in sync (all 5 prompts have been pushed with the **production** label).

**CLI (push from code after editing prompts):** From repo root:
```bash
bash scripts/update_langfuse_prompts_cli.sh
```
Requires `.env` with `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY`. Creates new prompt versions with the **production** label. Verify: `npx langfuse-cli --env .env api prompts list`.

**UI:** Edit the 5 prompts in the Langfuse dashboard; Save; add the **production** label to the new version. No app redeploy needed — the running app picks up changes (cache ~60s). See [LANGFUSE_SETUP.md](LANGFUSE_SETUP.md).

Prompt reference: [LEGAL_RESEARCH_PROMPTS_V4.md](LEGAL_RESEARCH_PROMPTS_V4.md). CLI details: [CLI_LANGFUSE_RAILWAY.md](CLI_LANGFUSE_RAILWAY.md).

### 2. Railway (A7) — CLI or dashboard

**Option A — CLI:** From repo root (with `railway login` and project linked):
```bash
bash scripts/railway_setup_volume_and_vars.sh
```
Or manually: `railway volume add --mount-path /app/data`. Optionally: `railway variables --set OPENAI_MODEL=gpt-4.1-mini`.

**Option B — Dashboard:** Add a volume at **`/app/data`**; optionally **`/app/reports`** and **OPENAI_MODEL=gpt-4.1-mini**.

### 3. Manual / local verification

- **Docker:** Run `docker compose up --build`. Confirm http://localhost:8000/health and http://localhost:8000/docs; if the backend container exits, run without `-d` to see logs and ensure `.env` is present.
- **E2E:** Run a full session (start → plan → execute tasks → report) with real API keys in `.env`.
- **Langfuse fallback:** Temporarily set `LANGFUSE_SECRET_KEY=invalid` and run a session; it should complete using inline prompts.
- **Push:** When satisfied, `git push origin main` (your branch is ahead by several commits).

---

## Quick reference

| Area        | Where        | Action |
|------------|--------------|--------|
| Prompts    | CLI or UI    | `bash scripts/update_langfuse_prompts_cli.sh` (applies production); or edit in Langfuse UI |
| Persistence| CLI or UI    | `railway volume add -m /app/data` or Railway dashboard |
| Model      | Railway vars | `railway variables --set OPENAI_MODEL=gpt-4.1-mini` (optional) |
| Smoke test | Local/Docker | Health, /docs, full session with API keys |
| Publish    | Git          | `git push origin main` after review |
