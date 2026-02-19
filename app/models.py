import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    status: Literal["pending", "in_progress", "done", "failed"] = "pending"
    tool_used: str | None = None
    result: str | None = None
    reflection: str | None = None
    sources: list[str] = Field(default_factory=list)


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
