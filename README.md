# LexAgent — Legal Research AI Agent

A legal research AI agent that takes a research goal, breaks it into actionable tasks, executes them using real web search tools, and produces a structured markdown report.

### Project background

This started as a weekend prototype to see how far a manual agent loop could get on real legal research without framework overhead. The main challenges were: (1) keeping context small enough to stay within token budgets across multiple tasks, and (2) making Tavily queries specific enough to get regulation-level detail. The current design — compressed context notes and Langfuse-versioned prompts — emerged from iterating on both. PDF ingestion and RAG were deliberately excluded; they are the obvious next layer but shipping them half-finished would make the demo worse, not better.

## Features

- **Agent Loop** — Built manually (no LangChain, LangGraph, AutoGen, or CrewAI)
- **Context Compression** — Raw search results are never stored; only 2–3 sentence summaries are retained
- **Langfuse Observability** — Full tracing of every LLM call with token usage and latency
- **Persistent Sessions** — Resume research sessions from past runs
- **Markdown Reports** — Professional legal research reports saved to disk
- **Dual Frontends** — Streamlit (Python) or React (Vite + TypeScript)

---

## Prerequisites

- Python 3.11+
- **Either** [UV](https://docs.astral.sh/uv/) **or** venv + pip (see Quick Start below)
- Node.js 18+ (for React frontend only)
- API keys: OpenAI, Tavily; Langfuse recommended for tracing (agent falls back to inline prompts if unreachable)

---

## Quick Start

You can use **UV** (default) or **venv + pip**; both work with the same `requirements.txt`. We keep a single toolchain (UV or pip) to avoid extra complexity; Poetry is not required.

### Option A — UV (recommended)

#### 1. Clone and install

```bash
git clone <repo>
cd lexagent
uv sync
```

#### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
LANGFUSE_SECRET_KEY=sk-lf-...   # Optional
LANGFUSE_PUBLIC_KEY=pk-lf-...  # Optional
LEXAGENT_API_URL=http://localhost:8000
OPENAI_MODEL=gpt-4o-mini
```

#### 3. Initialize Langfuse prompts (if using Langfuse)

```bash
uv run python app/init_langfuse_prompts.py
```

#### 4. Run the application

**Terminal 1 — Backend**

```bash
make backend
# or: uv run uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Frontend (choose one)**

```bash
# Option A: Streamlit
make frontend
# UI: http://localhost:8501

# Option B: React
make react
# UI: http://localhost:5173
```

---

### Option B — venv + pip

Use this if you prefer standard Python venv and pip (no UV installed).

#### 1. Clone and create venv

```bash
git clone <repo>
cd lexagent
python3 -m venv .venv
```

**Activate the venv:**

- macOS/Linux: `source .venv/bin/activate`
- Windows (cmd): `.venv\Scripts\activate.bat`
- Windows (PowerShell): `.venv\Scripts\Activate.ps1`

#### 2. Install dependencies

```bash
pip install -r requirements.txt
```

#### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your API keys (same as in Option A).

#### 4. Initialize Langfuse prompts (if using Langfuse)

```bash
python app/init_langfuse_prompts.py
```

#### 5. Run the application

**Terminal 1 — Backend**

```bash
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Frontend (choose one)**

```bash
# Streamlit
streamlit run frontend/ui.py
# UI: http://localhost:8501

# Or React (requires Node.js)
cd frontend-react && npm install && npm run dev
# UI: http://localhost:5173
```

*Note: The Makefile uses `uv run`; for a pip-only setup use the commands above (no `make` required).*

### Local Docker (API + React, optional Streamlit)

Run the backend (API + React) in Docker:

```bash
docker compose up --build backend
```

- **Backend + React**: http://localhost:8000 (API and React UI)
- Ensure `.env` contains `OPENAI_API_KEY` and `TAVILY_API_KEY`

To also run the Streamlit UI in Docker (pointing at the backend):

```bash
docker compose up --build
```

- **Backend + React**: http://localhost:8000  
- **Streamlit**: http://localhost:8501 (uses `LEXAGENT_API_URL=http://backend:8000`)

Sessions and reports persist when you mount volumes (default: `./data`, `./reports`). The same setup runs locally without Docker: `make backend` and `make frontend` (or `make dev`).

---

## How the Agent Loop Works

1. **Goal Input** — User submits a legal research goal via the UI
2. **Planning** — LLM decomposes the goal into 3–6 specific research tasks
3. **Execution** — For each task:
   - Refine the search query using task context + prior research
   - Execute web search via Tavily API
   - Compress raw results into a 2–3 sentence summary (never stored)
   - Reflect on findings and update context notes
   - Mark task as done
4. **Report** — Synthesize a markdown report from accumulated context
5. **Persistence** — Session state saved as JSON; users can resume anytime

**Context:** Raw search results (~10–50KB per task) are compressed to 2–3 sentences (~150–200 chars) before being appended to `context_notes`. For a 5-task session that’s ~1,000 chars of notes vs ~250KB of raw results (~250× compression). Token growth is linear in task count but small. The combined `context_notes` blob is capped at 8,000 chars in the executor and 12,000 in the report step to avoid overflowing the prompt.

---

### Failure modes and resilience

- **Thin Tavily results:** The reflect step evaluates whether the task was adequately answered; gaps are recorded in `context_notes` and influence later queries.
- **Task execution failure:** `task.status` is set to `in_progress` and the session is saved *before* running the search. A crash mid-task leaves a recoverable state; the failed task can be retried.
- **Task marked failed:** The agent continues to the next pending task; the failed task stays in session state and is visible in the UI.
- **Langfuse unreachable:** The agent falls back to inline prompt copies in `app/agent.py`; execution continues, tracing is unavailable until connectivity returns.
- **OpenAI/Tavily timeout:** The current task fails (see Known Limitations); session remains resumable.

## Architecture

```
lexagent/
├── app/
│   ├── agent.py              # Agent loop: state transitions, no framework hidden state
│   ├── main.py               # FastAPI: thin HTTP layer, delegates to agent
│   ├── models.py             # Pydantic: Task + AgentState with Literal status enum
│   ├── security.py           # Input validation: regex patterns, length limits, null-byte checks
│   ├── storage.py            # JSON persistence: auditable, swappable for DB
│   ├── tools.py              # Tavily search + report writer
│   └── init_langfuse_prompts.py
├── frontend/
│   └── ui.py                 # Streamlit UI (optional in Docker)
├── frontend-react/            # React + Vite + TypeScript (served at / in Docker)
├── docs/                      # Project documentation
├── data/                      # Session JSON (runtime; use volume in production)
├── reports/                   # Markdown reports (runtime)
├── transcript.md             # Example session transcript
├── Makefile                  # Development commands
└── pyproject.toml
```

**Why key modules are separate:** `agent.py` vs `main.py` keeps HTTP concerns out of the agent loop so you can test planning and execution without a server. `security.py` is isolated so guardrails can be unit-tested and tightened without touching business logic. `storage.py` exposes a small interface (`save_session`, `load_session`, `list_sessions`, `delete_session`) so swapping to Postgres/SQLite is a matter of reimplementing four functions.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/agent/start` | Create session, generate plan |
| GET | `/agent/{id}` | Get session state |
| GET | `/agent/{id}/report` | Get report markdown |
| POST | `/agent/{id}/execute` | Execute next task |
| GET | `/sessions` | List all sessions |
| DELETE | `/agent/{id}` | Delete session |

---

## Development

### Commands

```bash
make help          # List all commands
make test          # Python backend tests
make react-test    # React frontend tests
make test-all      # All tests
make lint          # Ruff linter
make lint-fix      # Auto-fix lint issues
make react-build   # Build React for production
make clean         # Remove sessions and reports
```

### Linting

```bash
uv run ruff check app/ frontend/
uv run ruff check --fix app/ frontend/
```

---

## Observability and prompt management

Every session produces a trace in Langfuse: per-task sub-spans, token usage, latency, and the prompt version used for each generation. **Prompt workflow:** edit in Langfuse UI → save → apply `production` label; the running app picks up changes within the SDK cache TTL (~60s). **Fallback:** if Langfuse is unreachable, the agent uses inline prompt copies in `app/agent.py` so it never fails solely due to observability.

## Documentation

| Document | Description |
|----------|-------------|
| [docs/TESTING.md](docs/TESTING.md) | Testing guide (Python + React) |
| [docs/EVALUATION.md](docs/EVALUATION.md) | Evaluation design and per-scenario criteria |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Deployment (Railway, Docker, local) |
| [docs/LANGFUSE_SETUP.md](docs/LANGFUSE_SETUP.md) | Langfuse prompt management |
| [docs/SECURITY.md](docs/SECURITY.md) | Security guardrails |
| [docs/BEST_PRACTICES.md](docs/BEST_PRACTICES.md) | Development best practices |
| [transcript.md](transcript.md) | Example session transcript |
| [docs/REMAINING_TASKS.md](docs/REMAINING_TASKS.md) | What’s done vs remaining (Langfuse, Railway, manual checks) |
| [docs/CLI_LANGFUSE_RAILWAY.md](docs/CLI_LANGFUSE_RAILWAY.md) | Update Langfuse prompts and Railway (volumes/vars) via CLI |
| [frontend-react/README.md](frontend-react/README.md) | React frontend details |

---

## Evaluation strategy

- **Per-scenario checklists:** See [docs/EVALUATION.md](docs/EVALUATION.md) for required elements and Pass/Partial/Fail criteria for each of the five scenarios.
- **LLM-as-judge (optional):** After a session, prompt GPT-4 to rate the report 1–5 on factual accuracy, legal specificity, source attribution, completeness; store in Langfuse linked to prompt version.
- **Regression:** Re-run evaluation scenarios when prompt versions change; compare against gold reports.
- **Hallucination detection:** Cross-reference article numbers in the report against source URLs in research notes.

## Evaluation scenarios

1. **GDPR AI Compliance** — Article 5, 25, 32; at least one BDSG reference; ≥3 source URLs; no hallucinated article numbers.
2. **EU AI Act high-risk** — Article 9, 13, 16; provider vs deployer; reference to EUR-Lex or official EU source.
3. **BRAO / AI in legal practice** — §43a BRAO, §2 BRAO, Verschwiegenheitspflicht; AI-assisted vs AI-replacing judgment.
4. **Employee monitoring (BDSG)** — §26 BDSG, Betriebsrat, proportionality.
5. **AI-generated contracts** — BGB §305, §§133/157; absence of specific AI-contract law; human review recommendation.

## AI assistants used in development

- **Claude / Cursor:** Refactoring the execute_task flow into the 4-step pattern (refine → search → compress → reflect); drafting security regex patterns; React component structure. Suggestions to combine compress and reflect into one prompt were rejected — the isolated design prevents the model from rubber-stamping its own output.
- **GitHub Copilot:** Boilerplate for FastAPI endpoints and Pydantic models; test scaffolding.
- **Human oversight:** Agent loop state machine (pending → in_progress → done/failed); decision to set in_progress and save before search; Langfuse prompt versions and production label workflow; security pattern false-positive analysis; all trade-offs documented here and in docs.

## Trade-offs

- **No agent framework** — Explicit state machine and no hidden framework state; more boilerplate, full control and clear Langfuse tracing.
- **Single tool (Tavily)** — Every task uses web search; predictable execution path; synthesis still triggers a search call.
- **No RAG over private docs** — Public web only; extension path: add a document-search tool without changing the loop.
- **JSON persistence** — Sessions in `data/`; simple and auditable; not for high-concurrency production; swap via `storage.py` for SQLite/Postgres.
- **CORS** — Demo uses `allow_origins=["*"]` for evaluator convenience; production should restrict to known frontend origins.

## Known limitations

- **Security false positives:** Queries containing “act as”, “assume the role of”, or “roleplay” may be blocked; rephrase (e.g. “obligations of a data processor under GDPR Article 28”).
- **No retry logic:** Tavily or OpenAI timeouts fail the current task; session stays resumable.
- **Context cap:** `context_notes` is truncated at 8,000 chars in execution and 12,000 in the report for long sessions.

## License

MIT
