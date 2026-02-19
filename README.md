# LexAgent — Legal Research AI Agent

A legal research AI agent that takes a research goal, breaks it into actionable tasks, executes them using real web search tools, and produces a structured markdown report.

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
- [UV](https://docs.astral.sh/uv/) package manager
- Node.js 18+ (for React frontend only)
- API keys: OpenAI, Tavily, Langfuse (optional for tracing)

---

## Quick Start

### 1. Clone and install

```bash
git clone <repo>
cd lexagent
uv sync
```

### 2. Configure environment

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

### 3. Initialize Langfuse prompts (required)

```bash
uv run python app/init_langfuse_prompts.py
```

### 4. Run the application

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

**Key insight:** `context_notes` stores only compressed summaries, never raw search text. This keeps the context window flat regardless of task count.

---

## Architecture

```
lexagent/
├── app/
│   ├── agent.py              # LLM wrapper + agent loop
│   ├── main.py               # FastAPI application
│   ├── models.py             # Pydantic models
│   ├── security.py           # Input validation, prompt injection guardrails
│   ├── storage.py            # JSON persistence
│   ├── tools.py              # Tavily search + report writer
│   └── init_langfuse_prompts.py
├── frontend/
│   └── ui.py                 # Streamlit dashboard
├── frontend-react/            # React + Vite + TypeScript
├── docs/                      # Project documentation
├── data/                      # Session JSON (runtime)
├── reports/                   # Markdown reports (runtime)
├── transcript.md             # Example session transcript
├── Makefile                  # Development commands
└── pyproject.toml
```

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

## Documentation

| Document | Description |
|----------|-------------|
| [docs/TESTING.md](docs/TESTING.md) | Testing guide (Python + React) |
| [docs/LANGFUSE_SETUP.md](docs/LANGFUSE_SETUP.md) | Langfuse prompt management |
| [docs/SECURITY.md](docs/SECURITY.md) | Security guardrails |
| [docs/BEST_PRACTICES.md](docs/BEST_PRACTICES.md) | Development best practices |
| [docs/UPDATES.md](docs/UPDATES.md) | Recent improvements |
| [transcript.md](transcript.md) | Example session transcript |
| [frontend-react/README.md](frontend-react/README.md) | React frontend details |

---

## Evaluation Scenarios

1. **GDPR AI Compliance** — Report covers Article 5, 25, 32 with citations
2. **EU AI Act Risk Classification** — High-risk classification, conformity assessment
3. **German Legal Ethics (BRAO)** — §43e BRAO, data protection obligations
4. **German vs EU Data Protection** — BDSG §22, §26 vs GDPR comparison
5. **AI-Generated Legal Documents** — Landmark cases with implications

---

## Trade-offs

- **No RAG** — Tavily returns current legal content; static docs become outdated
- **No agent framework** — Full control over prompts and context
- **JSON storage** — Human-readable, no DB setup
- **Streamlit + React** — Streamlit for rapid iteration; React for production UI

---

## License

MIT
