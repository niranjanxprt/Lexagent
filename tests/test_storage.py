"""Tests for app.storage: save_session, load_session round-trip."""

import pytest

from app import storage
from app.models import AgentState, Task


def test_save_and_load_session(tmp_path):
    storage.DATA_DIR = tmp_path / "data"
    task = Task(title="My task", description="Do research")
    state = AgentState(goal="Research GDPR", tasks=[task])
    storage.save_session(state)
    loaded = storage.load_session(state.session_id)
    assert loaded is not None
    assert loaded.goal == state.goal
    assert len(loaded.tasks) == 1
    assert loaded.tasks[0].title == "My task"


def test_load_session_missing_returns_none(tmp_path):
    storage.DATA_DIR = tmp_path / "data"
    assert storage.load_session("nonexistent-id") is None
