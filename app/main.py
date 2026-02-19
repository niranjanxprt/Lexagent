from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from app.agent import execute_task, generate_final_report, generate_plan
from app.models import AgentState, ExecuteResponse, GoalRequest
from app.storage import delete_session, list_sessions, load_session, save_session
from app.security import validate_goal, PromptInjectionError

# Load .env explicitly with override
env_file = Path(__file__).parent.parent / ".env"
load_dotenv(env_file, override=True)

app = FastAPI(
    title="LexAgent API",
    description="Legal Research AI Agent",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------


@app.get("/health")
def health_check():
    """Simple health check for monitoring and load balancers."""
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# POST /agent/start
# ---------------------------------------------------------------------------


@app.post("/agent/start", response_model=AgentState, status_code=201)
def start_agent(request: GoalRequest):
    """
    Initialize a new agent session and generate the research plan.
    Validates research goal for prompt injection attacks.
    Returns the full AgentState with tasks populated.
    """
    try:
        # Validate goal for prompt injection and suspicious content
        validated_goal = validate_goal(request.goal)
    except PromptInjectionError as e:
        raise HTTPException(status_code=400, detail=f"Invalid goal: {str(e)}")

    state = AgentState(goal=validated_goal)
    state.mode = "plan"

    tasks = generate_plan(validated_goal, state.session_id)
    state.tasks = tasks
    state.mode = "execute"

    save_session(state)
    return state


# ---------------------------------------------------------------------------
# GET /agent/{session_id}
# ---------------------------------------------------------------------------


@app.get("/agent/{session_id}", response_model=AgentState)
def get_session(session_id: str):
    """Return the current state of an agent session."""
    state = load_session(session_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return state


# ---------------------------------------------------------------------------
# GET /agent/{session_id}/report
# ---------------------------------------------------------------------------


@app.get("/agent/{session_id}/report")
def get_report(session_id: str):
    """Return raw markdown content for a completed session's report."""
    state = load_session(session_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Session not found")
    if not state.final_report_path:
        raise HTTPException(status_code=404, detail="Report not yet generated")
    try:
        with open(state.final_report_path) as f:
            content = f.read()
        return Response(content=content, media_type="text/markdown")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Report file not found")


# ---------------------------------------------------------------------------
# POST /agent/{session_id}/execute
# ---------------------------------------------------------------------------


@app.post("/agent/{session_id}/execute", response_model=ExecuteResponse)
def execute_step(session_id: str):
    """
    Execute the next pending task in the session.
    Designed for step-by-step execution (the frontend calls this repeatedly).
    """
    state = load_session(session_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Session not found")
    if not state.is_active:
        raise HTTPException(status_code=400, detail="Session is already complete")

    # Find the next pending task
    pending_tasks = [t for t in state.tasks if t.status == "pending"]

    if not pending_tasks:
        # All tasks done — generate report
        report_path = generate_final_report(state)
        state.final_report_path = report_path
        state.is_active = False
        state.mode = "done"
        save_session(state)
        return ExecuteResponse(
            session_id=state.session_id,
            current_step=state.current_step,
            task_executed=None,
            is_done=True,
            message=f"All tasks complete. Report saved to {report_path}",
        )

    # Execute the first pending task
    task = pending_tasks[0]
    task.status = "in_progress"
    save_session(state)

    executed_task = execute_task(task, state)

    # Update the task in state.tasks by index
    for i, t in enumerate(state.tasks):
        if t.id == executed_task.id:
            state.tasks[i] = executed_task
            break

    state.current_step += 1
    save_session(state)

    return ExecuteResponse(
        session_id=state.session_id,
        current_step=state.current_step,
        task_executed=executed_task,
        is_done=False,
        message=f"Executed: {executed_task.title}",
    )


# ---------------------------------------------------------------------------
# GET /sessions
# ---------------------------------------------------------------------------


@app.get("/sessions", response_model=list[AgentState])
def get_sessions():
    """List all stored agent sessions."""
    return list_sessions()


# ---------------------------------------------------------------------------
# DELETE /agent/{session_id}
# ---------------------------------------------------------------------------


@app.delete("/agent/{session_id}", status_code=204)
def remove_session(session_id: str):
    """Delete a session and its associated data."""
    success = delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
