import os
from datetime import datetime
from pathlib import Path

from tavily import TavilyClient

REPORTS_DIR = Path(__file__).parent.parent / "reports"


def _ensure_reports_dir() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def search_web(query: str) -> dict:
    """
    Search the web using Tavily and return raw results.
    The agent layer is responsible for compressing these into
    context notes — raw results are never stored in AgentState.
    """
    client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY", ""))
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
    _ensure_reports_dir()
    filename = f"{session_id}.md"
    path = REPORTS_DIR / filename
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    full_content = f"# Legal Research Report\n\n**Goal:** {goal}\n\n**Generated:** {timestamp}\n\n---\n\n{content}"
    with open(path, "w", encoding="utf-8") as f:
        f.write(full_content)
    return str(path)
