import json
from pathlib import Path

from app.models import AgentState

DATA_DIR = Path(__file__).parent.parent / "data"


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def save_session(state: AgentState) -> None:
    _ensure_data_dir()
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
    _ensure_data_dir()
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
