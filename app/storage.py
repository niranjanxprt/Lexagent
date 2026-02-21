import json
import os
from pathlib import Path

from app.models import AgentState

# Configurable via env for Railway (e.g. volume at /app/persist → LEXAGENT_DATA_DIR=/app/persist/data)
_DEFAULT_DATA = Path(__file__).parent.parent / "data"
DATA_DIR = Path(os.environ.get("LEXAGENT_DATA_DIR", str(_DEFAULT_DATA)))


def save_session(state: AgentState) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / f"{state.session_id}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state.model_dump(), f, indent=2)


def load_session(session_id: str) -> AgentState | None:
    path = DATA_DIR / f"{session_id}.json"
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return AgentState(**data)


def list_sessions() -> list[AgentState]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    sessions = []
    for file in DATA_DIR.glob("*.json"):
        with open(file, encoding="utf-8") as f:
            data = json.load(f)
        sessions.append(AgentState(**data))
    return sessions


def delete_session(session_id: str) -> bool:
    path = DATA_DIR / f"{session_id}.json"
    if not path.exists():
        return False
    path.unlink()
    return True
