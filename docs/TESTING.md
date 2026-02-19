# LexAgent Testing Guide

## Quick Tests (No API Keys)

### Python backend

```bash
make test
```

This runs:
- Model validation (Task, AgentState)
- Storage (save, load session)
- Basic imports

### React frontend

```bash
make react-test
```

Runs Vitest suite: types, API config, utils, components, integration.

### All tests

```bash
make test-all
```

---

## Linting

```bash
make lint
# or
uv run ruff check app/ frontend/
```

---

## Full E2E (Requires API Keys)

### 1. Setup

```bash
cp .env.example .env
# Add OPENAI_API_KEY, TAVILY_API_KEY
uv run python app/init_langfuse_prompts.py
```

### 2. Start backend

```bash
make backend
```

Verify: `curl http://localhost:8000/health` → `{"status":"ok"}`

### 3. Start frontend

```bash
# Streamlit
make frontend
# or React
make react
```

### 4. Manual test flow

1. Enter goal: e.g. "Research EU AI Act Article 3 definition of legal AI"
2. Click **Generate Research Plan**
3. Click **Execute Next Step** (or enable Auto-run)
4. Verify tasks complete, report appears
5. Download report, check `reports/` directory

### 5. Verify persistence

```bash
ls data/*.json
ls reports/*.md
```

---

## What Gets Tested

| Area | Python | React |
|------|--------|-------|
| Models | Task, AgentState | Types (Task, AgentState, etc.) |
| Storage | save, load, list | — |
| API | — | Endpoint config, mocks |
| Components | — | NewSession, etc. |
| Integration | — | Session flow, state transitions |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `OPENAI_API_KEY not set` | Add to `.env` |
| `Tavily API key missing` | Add `TAVILY_API_KEY` to `.env` |
| `Prompt not found` | Run `uv run python app/init_langfuse_prompts.py` |
| Port 8000 in use | Use `--port 8001`, update `LEXAGENT_API_URL` |
| React build fails | Run `npm install` in `frontend-react` |

---

## Performance

- First API call (planning): ~3–5 s
- Each task execution: ~15–30 s
- Final report: ~10 s
- Typical 5-task session: ~2–3 min
