"""Tests for app.models: Task, AgentState, ResearchPlan, ReflectResult."""

import pytest
from pydantic import ValidationError

from app.models import AgentState, ReflectResult, ResearchPlan, Task, TaskDraft


def test_task_construction_and_dump():
    task = Task(title="Test task", description="Do something")
    assert task.title == "Test task"
    assert task.description == "Do something"
    assert task.status == "pending"
    assert task.id
    d = task.model_dump()
    assert d["title"] == "Test task"
    assert d["status"] == "pending"


def test_task_round_trip():
    task = Task(title="A", description="B", status="done", result="Summary")
    d = task.model_dump()
    task2 = Task(**d)
    assert task2.title == task.title
    assert task2.status == "done"
    assert task2.result == "Summary"


def test_agent_state_construction_and_dump():
    task = Task(title="T", description="D")
    state = AgentState(goal="Research X", tasks=[task])
    assert state.goal == "Research X"
    assert len(state.tasks) == 1
    assert state.tasks[0].title == "T"
    assert state.mode == "plan"
    assert state.session_id
    d = state.model_dump()
    assert d["goal"] == "Research X"
    assert len(d["tasks"]) == 1


def test_agent_state_round_trip():
    task = Task(title="T", description="D", status="in_progress")
    state = AgentState(goal="Goal", tasks=[task], mode="execute")
    d = state.model_dump()
    state2 = AgentState(**d)
    assert state2.goal == state.goal
    assert state2.mode == "execute"
    assert state2.tasks[0].status == "in_progress"


def test_research_plan_valid():
    plan = ResearchPlan(
        tasks=[
            TaskDraft(title="Task 1", description="Desc 1"),
            TaskDraft(title="Task 2", description="Desc 2"),
        ]
    )
    assert len(plan.tasks) == 2
    assert plan.tasks[0].title == "Task 1"
    d = plan.model_dump()
    assert len(d["tasks"]) == 2


def test_research_plan_empty_tasks_raises():
    with pytest.raises(ValidationError):
        ResearchPlan(tasks=[])


def test_reflect_result_valid():
    r = ReflectResult(status="fully_addressed", gap="")
    assert r.status == "fully_addressed"
    assert r.gap == ""
    r2 = ReflectResult(status="partially_addressed", gap="Missing X")
    assert r2.gap == "Missing X"
    d = r2.model_dump()
    assert d["status"] == "partially_addressed"


def test_reflect_result_round_trip():
    r = ReflectResult(status="not_addressed", gap="No sources")
    r2 = ReflectResult(**r.model_dump())
    assert r2.status == r.status
    assert r2.gap == r.gap
