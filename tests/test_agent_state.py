"""Tests for agent state transitions: task status in_progress -> done with save/load."""

import pytest

from app import storage
from app.models import AgentState, Task


def test_state_transition_in_progress_then_done_save_load(tmp_path):
    storage.DATA_DIR = tmp_path / "data"
    task = Task(title="Task 1", description="Research X", status="pending")
    state = AgentState(goal="Goal", tasks=[task])
    state.tasks[0].status = "in_progress"
    storage.save_session(state)
    loaded = storage.load_session(state.session_id)
    assert loaded.tasks[0].status == "in_progress"

    state.tasks[0].status = "done"
    state.tasks[0].result = "Summary"
    state.tasks[0].sources = ["https://example.com"]
    storage.save_session(state)
    loaded2 = storage.load_session(state.session_id)
    assert loaded2.tasks[0].status == "done"
    assert loaded2.tasks[0].result == "Summary"
    assert loaded2.tasks[0].sources == ["https://example.com"]
