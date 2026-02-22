# LexAgent Testing Guide

## Test philosophy

The agent has **deterministic** parts (JSON parsing, state transitions, storage) and **non-deterministic** parts (LLM responses, Tavily results). Tests focus on the deterministic behavior; the non-deterministic behavior is validated manually or via scenario checklists (see evaluation docs).

## Quick tests (no API keys)

### Python backend

```bash
make test
```

Covers: model validation (Task, AgentState), storage save/load, and that core imports (including agent and security) work.

#### Backend test scope

Pytest covers: models (Task, AgentState, ResearchPlan, ReflectResult), storage save/load round-trip, tools.save_report (file content and metadata), security (validate_goal, validate_search_results, including that search results allow benign "You are now…" text), and agent state transitions (task status in_progress/done with save/load). Real LLM and Tavily behavior are left to manual runs and evaluation docs.

### React frontend

```bash
make react-test
```

Runs Vitest: types, API config, utils, components, integration.

### All tests

```bash
make test-all
```

Runs both Python and React tests.

---

## Linting

```bash
make lint
# or
uv run ruff check app/
```

Fix auto-fixable issues: `make lint-fix`.

---

## Key behaviors to test (when adding tests)

- **State transitions:** `task.status` is set to `in_progress` and the session is saved *before* calling the search. A crash during search leaves the task in a recoverable state, not a phantom "pending".
- **Security:** `validate_goal()`, `validate_context_notes()`, and `validate_search_results()` are used at the boundaries; injection patterns should be unit-tested in `security.py`.
- **Context size:** After execution, `context_notes` should contain only compressed summaries (e.g. no raw Tavily blobs); length expectations can be asserted in tests.
- **Storage round-trip:** Save and load a session; all fields (goal, tasks, context_notes, etc.) should match.

---

## Full E2E (requires API keys)

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

## Integration Regression Eval (requires API keys)

`scripts/run_simple_eval.py` runs the full agent pipeline against 3 predefined legal goals and checks for required keywords in each report. This is the most impactful eval — it validates the entire plan → execute → report loop with real API calls and requires no Langfuse setup.

```bash
uv run python scripts/run_simple_eval.py
# Run only 1 item for a quick smoke test:
uv run python scripts/run_simple_eval.py --limit 1
```

Requires `OPENAI_API_KEY` and `TAVILY_API_KEY` in `.env`. See [EVALUATION.md](EVALUATION.md) for the full strategy.

### Langfuse dataset eval (optional)

`scripts/run_eval.py` scores the `reflect` prompt against golden examples in Langfuse. Requires Langfuse credentials and the dataset to exist first:

```bash
# Step 1 — create the dataset (run once)
uv run python scripts/create_eval_dataset.py
# Step 2 — run eval and post scores to Langfuse
uv run python scripts/run_eval.py
```

Scores appear in the Langfuse dashboard under **Datasets → lexagent-eval-v1**.

---

## Performance

- First API call (planning): ~3–5 s
- Each task execution: ~15–30 s
- Final report: ~10 s
- Typical 5-task session: ~2–3 min
