import os
from datetime import datetime
from pathlib import Path

from tavily import TavilyClient

from app.context import get_api_keys

# Configurable via env for Railway (e.g. volume at /app/persist → LEXAGENT_REPORTS_DIR=/app/persist/reports)
_DEFAULT_REPORTS = Path(__file__).parent.parent / "reports"
REPORTS_DIR = Path(os.environ.get("LEXAGENT_REPORTS_DIR", str(_DEFAULT_REPORTS)))


def search_web(query: str) -> dict:
    """
    Search the web using Tavily and return raw results.
    The agent layer is responsible for compressing these into
    context notes — raw results are never stored in AgentState.
    Uses TAVILY_API_KEY from env, or request-scoped override from context.
    """
    api_keys = get_api_keys()
    tavily_key = api_keys.get("tavily") or os.environ.get("TAVILY_API_KEY", "")
    client = TavilyClient(api_key=tavily_key)
    response = client.search(
        query=query,
        max_results=5,
        include_raw_content=False,
    )
    results = []
    for r in response.get("results", []):
        results.append({
            "title": r["title"],
            "url": r["url"],
            "content": r["content"],
        })
    return {
        "query": query,
        "results": results,
    }


def save_report(session_id: str, goal: str, content: str) -> str:
    """
    Save a markdown report to /reports/{session_id}.md.
    Returns the file path as a string.
    """
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{session_id}.md"
    path = REPORTS_DIR / filename
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    full_content = f"# Legal Research Report\n\n**Goal:** {goal}\n\n**Generated:** {timestamp}\n\n---\n\n{content}"
    with open(path, "w", encoding="utf-8") as f:
        f.write(full_content)
    return str(path)
