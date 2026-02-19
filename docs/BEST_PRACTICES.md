# LexAgent Best Practices

## Development

### Python

- Use `uv sync` for dependencies
- Run `make lint` before committing
- Use type hints (Python 3.10+ style: `str | None`)
- Keep prompts in Langfuse; avoid hardcoding in code

### React

- Use `npm run lint` (tsc --noEmit) before committing
- Prefer `lib/api.ts` fetch over axios for API calls
- Keep components focused; extract shared logic to hooks/utils

### Security

- Validate all user inputs before LLM calls (see `app/security.py`)
- Never log raw API keys
- Use `validate_goal()` at API entry; `validate_context_notes()` in agent

### Context management

- Never store raw search results in `context_notes`
- Always compress via LLM before appending
- Keep `context_notes` flat; avoid nested structures

## Testing

- Run `make test-all` before pushing
- Mock external APIs (Tavily, OpenAI) in unit tests
- Use `make test` for quick Python smoke test

## Deployment

- Set `CORS_ORIGINS` for production (avoid `*`)
- Use `GET /health` for load balancer health checks
- Ensure Langfuse prompts are initialized (`init_langfuse_prompts.py`)

## Documentation

- Update README when adding features
- Keep `docs/` in sync with code changes
- Use `transcript.md` for example sessions
