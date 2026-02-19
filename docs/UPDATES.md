# LexAgent Updates & Features

## Recent Improvements

### React frontend

- Full feature parity with Streamlit UI
- Session management, task execution, report download
- Auto-run mode for batch execution
- Markdown rendering with GFM (tables, links, code blocks)
- Vitest test suite

### Security

- Prompt injection guardrails (`app/security.py`)
- Input validation at API entry and in agent
- Length limits and pattern detection

### Langfuse

- Prompts externalized to Langfuse for centralized management
- `init_langfuse_prompts.py` for one-time setup
- Tracing for all LLM calls

### API

- `GET /health` for monitoring
- `GET /agent/{id}/report` for report fetching

### Documentation

- Consolidated docs in `docs/`
- Single README per frontend
- Best practices guide
