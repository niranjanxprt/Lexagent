import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class TaskDraft(BaseModel):
    """Validated output from generate-plan LLM call (title + description only)."""

    title: str
    description: str


class ResearchPlan(BaseModel):
    """Validated JSON envelope from generate-plan. Bounds prevent empty or runaway plans."""

    tasks: list[TaskDraft] = Field(min_length=1, max_length=8)


class ReflectResult(BaseModel):
    """Validated JSON from reflect step. status is Literal for strict routing; gap default for fully_addressed."""

    status: Literal["fully_addressed", "partially_addressed", "not_addressed"]
    gap: str = ""


class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    status: Literal["pending", "in_progress", "done", "failed"] = "pending"
    tool_used: str | None = None
    result: str | None = None
    reflection: str | None = None
    reflect_status: Literal["fully_addressed", "partially_addressed", "not_addressed"] = "fully_addressed"
    sources: list[str] = Field(default_factory=list)
    failure_reason: str | None = None


class AgentState(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    goal: str
    tasks: list[Task] = Field(default_factory=list)
    context_notes: list[str] = Field(default_factory=list)
    current_step: int = 0
    is_active: bool = True
    mode: Literal["plan", "execute", "done"] = "plan"
    final_report_path: str | None = None
    created_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )


class GoalRequest(BaseModel):
    goal: str


class ExecuteResponse(BaseModel):
    session_id: str
    current_step: int
    task_executed: Task | None = None
    is_done: bool
    message: str
