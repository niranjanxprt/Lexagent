# LexAgent Architecture

## Overview

LexAgent is a legal research agent built with a manual agent loop (no LangChain/LangGraph). It decomposes a research goal into tasks, executes each with a web search, compresses results, reflects on completeness, and generates a Markdown report.

**Stack:** FastAPI (Python 3.11) + React (Vite + TypeScript) + Langfuse + Tavily + OpenAI

---

## System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                         Browser                                   │
│                  React (Vite + TypeScript)                        │
│  localhost:5173 (make dev) or :8000 (prod / Docker)                 │
└────────────────────────────┬────────────────────────────────────┘
                             │ REST API
┌────────────────────────────▼────────────────────────────────────┐
│                   FastAPI (app/main.py)                          │
│  POST /agent/start   GET /agent/{id}   POST /agent/{id}/execute  │
│  GET /agent/{id}/report   DELETE /agent/{id}   GET /sessions      │
└────────┬───────────────────────┬────────────────────┬────────┘
         │                       │                      │
┌────────▼────────┐   ┌──────────▼──────────┐   ┌──────▼─────────┐
│  app/agent.py   │   │   app/storage.py     │   │ app/tools.py   │
│ (agent loop)   │   │ (JSON session store) │   │ (search+save)   │
└────────┬────────┘   └─────────────────────┘   └────────┬────────┘
         │                                                │
┌────────▼────────┐                            ┌──────────▼────────┐
│ Langfuse SDK   │                            │  Tavily API       │
│ (tracing +     │                            │  (web search)     │
│  prompt mgmt)  │                            └───────────────────┘
└────────┬────────┘
┌────────▼────────┐
│  OpenAI API     │
│  (gpt-4.1)      │
└─────────────────┘
```

---

## File Structure

```
lexagent/
├── app/
│   ├── agent.py               # Agent loop: plan, execute, reflect, report
│   ├── main.py                # FastAPI endpoints and request handling
│   ├── models.py              # Pydantic models (Task, AgentState, etc.)
│   ├── storage.py             # Session persistence (JSON files in data/)
│   ├── tools.py               # search_web (Tavily) + save_report
│   ├── security.py            # Input validation / prompt injection guards
│   ├── context.py             # Request-scoped API key overrides
│   └── init_langfuse_prompts.py  # Authoritative prompt definitions (5 prompts)
│
├── frontend-react/            # React + TypeScript UI (Vite)
│   ├── src/
│   │   ├── components/        # ResearchForm, TaskList, Report, etc.
│   │   └── lib/api.ts         # Typed API client
│   └── Dockerfile             # Build: npm run build:docker
│
├── scripts/
│   ├── create_eval_dataset.py # Create Langfuse eval dataset (golden examples)
│   ├── run_eval.py            # Run reflect eval against Langfuse dataset
│   ├── run_simple_eval.py     # End-to-end regression (full pipeline)
│   ├── eval_dataset.json     # Simple eval input/output pairs
│   ├── prompts/*.json        # JSON copies of prompts (synced to init file)
│   └── update_langfuse_prompts_cli.sh  # Push prompts to Langfuse
│
├── docs/                      # Documentation
├── data/                      # Session JSON files (gitignored)
├── reports/                   # Markdown report files (gitignored)
├── Dockerfile                 # Multi-stage: Node (React) → Python (serve both)
├── start.sh                   # Entrypoint: uvicorn on $PORT
└── railway.toml               # Railway deploy config
```

---

## Agent Loop (app/agent.py)

Each research session runs through this pipeline:

```
User goal
    │
    ▼
generate_plan()
  └─ Prompt: legal-research/generate-plan (gpt-4.1)
  └─ Output: ResearchPlan (3–6 Task objects, Pydantic-validated)
    │
    ▼ (for each task)
execute_task()
  │
  ├─ 1. refine-query prompt → search query (max 12 words)
  │
  ├─ 2. search_web(query)
  │     └─ Tavily API (max 5 results, 3-attempt retry with backoff)
  │     └─ @observe(name="search-web") → Langfuse span
  │
  ├─ 3. compress-results prompt → 2–4 sentence summary
  │     (sees ONLY raw Tavily output — isolation prevents confirmation bias)
  │
  ├─ 4. reflect prompt → ReflectResult (JSON: status + gap)
  │     └─ reflect_status / reflect_gap saved to Langfuse generation metadata
  │
  └─ 5. Append compressed summary to state.context_notes
         (raw results are NEVER stored)
    │
    ▼ (when all tasks done)
generate_final_report()
  └─ Prompt: legal-research/generate-report (gpt-4.1)
  └─ Input: all context_notes + task summaries + deduplicated URLs
  └─ Output: Markdown report saved to reports/{session_id}.md
```

---

## Data Models (app/models.py)

| Model | Purpose |
|-------|---------|
| `Task` | One research task: title, description, status, result, sources, reflect_status |
| `AgentState` | Full session: session_id, goal, tasks[], context_notes[], mode, final_report_path |
| `ResearchPlan` | LLM output for generate-plan: tasks[] (1–8, Pydantic-bounded) |
| `ReflectResult` | LLM output for reflect: status (Literal), gap string |
| `GoalRequest` | API input: goal string |
| `ExecuteResponse` | API response for /execute: session_id, current_step, task_executed, is_done |

**Task status lifecycle:** `pending` → `in_progress` → `done` | `failed`

**AgentState mode lifecycle:** `plan` → `execute` → `done`

---

## Prompt Architecture

All 5 prompts are defined in `app/init_langfuse_prompts.py` and managed in Langfuse.

| Prompt | Model | Purpose |
|--------|-------|---------|
| `legal-research/generate-plan` | gpt-4.1 (full) | Decompose goal into 3–6 tasks |
| `legal-research/refine-query` | gpt-4.1-mini | Generate web search query (max 12 words) |
| `legal-research/compress-results` | gpt-4.1-mini | Compress Tavily results to 2–4 sentences |
| `legal-research/reflect` | gpt-4.1-mini | Validate task completeness (JSON schema) |
| `legal-research/generate-report` | gpt-4.1 (full) | Synthesize final Markdown report |

**Model split rationale:** Plan and report use `gpt-4.1` (full) for quality. The three intermediate steps use `gpt-4.1-mini` for cost and speed. `_full_model()` in agent.py derives the full model name by stripping `-mini`/`-nano` suffixes from `OPENAI_MODEL`.

**Fallback:** If Langfuse is unreachable on cold start, `PROMPT_FALLBACKS` in `agent.py` provides identical inline copies. The `FallbackPrompt` class mimics the Langfuse compile interface.

---

## Security (app/security.py)

Input validation is applied **only at the API boundary** (user-submitted goal). LLM-generated content (task titles, context notes) is intentionally not validated — legal terminology like "execute a contract" would trigger false positives.

Validation checks: length (500 chars for goal), injection patterns (ignore instructions, system prompt, jailbreak, HTML tags, shell operators), null bytes, excessive control characters.

**Request-scoped API key isolation (`app/context.py`):** Per-request API key overrides (`X-OpenAI-API-Key`, `X-Tavily-API-Key` headers) are stored in a Python `ContextVar`, not in `os.environ`. This isolates key overrides to the current request context, making concurrent requests safe without race conditions.

See [SECURITY.md](SECURITY.md) for full pattern list and rationale.

---

## Deployment Topology

### Production (Railway)

```
Railway
└── Single container (Dockerfile multi-stage)
    ├── Stage 1: Node — npm run build:docker → ./static/
    └── Stage 2: Python — serves React at / and API at /agent/*
        └── uvicorn app.main:app --port $PORT
```

Sessions persist only with a Railway Volume at `/app/data`.

### Local Development

`make dev` (or `make run`): backend on :8000, React on :5173. No Docker required. To test the production image locally: `docker build -t lexagent .` then `docker run -p 8000:8000 --env-file .env lexagent` (see [DEPLOYMENT.md](DEPLOYMENT.md)).

---

## Environment Variables

| Variable | Required | Default | Notes |
|----------|----------|---------|-------|
| `OPENAI_API_KEY` | Yes | — | |
| `TAVILY_API_KEY` | Yes | — | |
| `LANGFUSE_SECRET_KEY` | Recommended | — | Falls back to inline prompts if missing |
| `LANGFUSE_PUBLIC_KEY` | Recommended | — | |
| `LANGFUSE_BASE_URL` | Optional | Langfuse cloud | Self-hosted only |
| `OPENAI_MODEL` | Optional | `gpt-4.1-mini` | Plan/report auto-upgrade to `gpt-4.1` |
| `PORT` | Railway only | 8000 | Set by Railway; do not override |
| `LEXAGENT_DATA_DIR` | Optional | `/app/data` | Override for Railway volume path |
| `LEXAGENT_REPORTS_DIR` | Optional | `/app/reports` | Override for Railway volume path |

Per-request key overrides via headers: `X-OpenAI-API-Key`, `X-Tavily-API-Key`.

---

## Key Design Decisions

**Execute-step retry:** `POST /agent/{session_id}/execute` retries `execute_task()` up to 3 times before marking the task `failed` and returning HTTP 500. This is separate from the Tavily-level retry (3 attempts with exponential backoff) inside `search_web()`.

**Partial report:** When all pending tasks are exhausted but some have `status == "failed"`, `generate_final_report()` still runs and produces a partial report. The response message is `"Partial report generated (N task(s) failed)."` Failed tasks remain visible in the session.

**OpenAI error handling:** `AuthenticationError` from OpenAI returns HTTP 401. `APIError` returns HTTP 503. Both are registered as global FastAPI exception handlers in `app/main.py`.

**No framework (LangChain / LangGraph):** The agent loop is ~50 lines in agent.py. A framework adds abstraction overhead and makes debugging harder. The manual loop makes every step visible and testable.

**Compression isolation:** The compress-results prompt sees only raw Tavily output — not the task goal or prior context. This prevents the model from "confirming" findings that are not in the actual search results (a common hallucination pattern).

**Raw results never stored:** Tavily returns 2–10KB per result. Storing raw results in `context_notes` would exhaust the context window after 2–3 tasks. Only 2–4 sentence summaries are kept.

**Context caps:** `context_notes` is truncated to 8000 chars before refine-query and 12000 chars before generate-report to avoid silent token overflow.

**JSON persistence:** Sessions are stored as `{session_id}.json` in `data/`. Simple, human-readable, no DB dependency. For production scale, replace `storage.py` with Postgres.

**Pydantic validation on LLM JSON outputs:** `call_llm_validated()` retries once with a correction message on parse/validation failure before raising. This catches transient model formatting errors without infinite loops.
