# LexAgent Best Practices

## Development

### Python

- Use `uv sync` for dependencies; run `make lint` before committing
- Use type hints (Python 3.11+ style: `str | None`)
- Keep prompts in Langfuse; inline fallbacks in `app/agent.py` are for cold-start only — keep them in sync with Langfuse

### React

- Use `npm run lint` (tsc --noEmit) before committing
- Prefer `lib/api.ts` fetch for API calls
- Keep components focused; extract shared logic to hooks/utils

### Security

- Validate at the boundary: `validate_goal()` at API entry; `validate_context_notes()` and `validate_search_results()` in the agent before using data in prompts
- Never log raw API keys; see `app/security.py` for patterns and known false-positive trade-offs

### Context management (important)

- **Never store raw search results in `context_notes`.** Tavily returns 2–10KB per result; storing it would blow the context after a few tasks. Always compress to 2–3 sentences via the compress-results prompt, then append only that summary.
- The compress step is deliberately isolated: it sees only raw Tavily output, not the task goal or prior context. That prevents the model from “confirming” findings that are not in the actual search results.
- The combined `context_notes` blob is capped (8k chars in execution, 12k in report) to avoid silent overflow for long sessions.

## Testing

- Run `make test-all` before pushing
- Mock Tavily/OpenAI in unit tests when testing agent logic
- See [TESTING.md](TESTING.md) for what to cover (state transitions, security, storage round-trip)

## Deployment

- Use `GET /health` for load balancer health checks
- For production, restrict CORS to known frontend origins (demo uses `["*"]` for convenience)
- Sessions and reports use `/app/data` and `/app/reports`; mount volumes there for persistence (e.g. Railway Volumes, Docker compose)
- See [DEPLOYMENT.md](DEPLOYMENT.md) and [RAILWAY_DEPLOY.md](RAILWAY_DEPLOY.md) for Railway and local Docker

## Documentation

- Update README when adding features; keep docs in sync with code
- Use `transcript.md` for example sessions; keep evaluation scenarios and success criteria in README or EVALUATION docs
