# Remaining Tasks (Post–Pre-Submission Work)

Summary of what is **done** in the repo vs what is **left for you** (manual or external).

---

## Done (in this repo)

- **Code:** `validate_search_results()` wired in; Langfuse fallback (`get_prompt_safe`); context length guards; `session_id` in `generate_plan()`; strategic comments; crash-recovery comment in `main.py`; `validate_all_variables` docstring.
- **Docker:** `frontend/` in image; `streamlit` service in docker-compose.
- **Docs:** README (background, failure modes, evaluation strategy, AI assistants, trade-offs, limitations, **Option A UV + Option B venv+pip**); DEPLOYMENT.md; EVALUATION.md; RAILWAY_DEPLOY; TESTING; BEST_PRACTICES; LOCALHOST_TEST_LINKS; transcript (4-task plan, footnote, imperfect reflection).
- **Tests:** `make test`, `make lint`, `make react-test` passing; Docker build succeeds.
- **Git:** All of the above committed (multiple commits on `main`).

---

## Remaining (for you to do)

### 1. Langfuse UI (Block D) — in Langfuse dashboard only

- **generate-plan:** Add to system message: *"All tasks must be research/search tasks. Do not include a final 'compile', 'synthesize', or 'write report' task — report generation is automatic."*
- **refine-query:** Add: return only the query string; prefer authoritative sources (eur-lex, gesetze-im-internet, regulators).
- **compress-results:** Add: preserve article/section references exactly (e.g. GDPR Art 5, BDSG §26).
- **reflect:** Add: one sentence; if fully addressed say so; if not, state the main gap.
- **generate-report:** Add: end with Sources section (key URLs); cite articles explicitly.
- Apply the **production** label to the version you want the app to use.
- Ensure each prompt has at least two versions if you want to demonstrate versioning.

### 2. Railway (A7) — in Railway dashboard

- Add a **volume** with mount path **`/app/data`** so sessions persist across redeploys.
- Optionally set **`OPENAI_MODEL=gpt-4o`** for stronger legal reasoning.
- Optionally add a volume for **`/app/reports`** if you want report files to persist.

### 3. Manual / local verification

- **Docker:** Run `docker compose up --build` (free port 8501 first if using Streamlit). Confirm http://localhost:8000/health and http://localhost:8000/docs; if the backend container exits, run without `-d` to see logs and ensure `.env` is present.
- **E2E:** Run a full session (start → plan → execute tasks → report) with real API keys in `.env`.
- **Langfuse fallback:** Temporarily set `LANGFUSE_SECRET_KEY=invalid` and run a session; it should complete using inline prompts.
- **Push:** When satisfied, `git push origin main` (your branch is ahead by several commits).

---

## Quick reference

| Area        | Where        | Action |
|------------|--------------|--------|
| Prompts    | Langfuse UI  | Edit 5 prompts, add text above, set `production` label |
| Persistence| Railway      | Volume at `/app/data` (and optionally `/app/reports`) |
| Model      | Railway vars | Optional: `OPENAI_MODEL=gpt-4o` |
| Smoke test | Local/Docker | Health, /docs, full session with API keys |
| Publish    | Git          | `git push origin main` after review |
