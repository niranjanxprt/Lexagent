"""
Request-scoped API key overrides from frontend.
When set, these override env vars for the current request.
Author: niranjanxprt (https://github.com/niranjanxprt)
"""
from contextvars import ContextVar

api_keys_ctx: ContextVar[dict | None] = ContextVar("api_keys", default=None)


def get_api_keys() -> dict:
    """Return current request's API key overrides."""
    return api_keys_ctx.get() or {}


def set_api_keys(openai_key: str | None = None, tavily_key: str | None = None) -> None:
    """Set API key overrides for current request."""
    ctx = dict(api_keys_ctx.get() or {})
    if openai_key and openai_key.strip():
        ctx["openai"] = openai_key.strip()
    if tavily_key and tavily_key.strip():
        ctx["tavily"] = tavily_key.strip()
    api_keys_ctx.set(ctx)
