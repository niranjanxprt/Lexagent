import json
import os

from dotenv import load_dotenv
from langfuse import get_client, observe
from langfuse.openai import openai

from app.context import get_api_keys
from app.models import AgentState, Task
from app.security import (
    PromptInjectionError,
    validate_context_notes,
)
from app.tools import save_report, search_web

load_dotenv()

langfuse = get_client()

# ---------------------------------------------------------------------------
# LLM wrapper
# ---------------------------------------------------------------------------


@observe(name="call-llm", as_type="generation")
def call_llm(
    messages: list,
    use_json: bool = False,
    trace_name: str | None = None,
    langfuse_prompt=None,
) -> str:
    """
    Wrapper around OpenAI chat completions.
    Langfuse @observe() automatically captures:
      - input messages
      - output content
      - token usage
      - latency

    Args:
        messages: List of message dicts for the LLM
        use_json: Whether to request JSON output format
        trace_name: Optional name for tracing
        langfuse_prompt: Optional Langfuse prompt object for linking to traces
    """
    api_keys = get_api_keys()
    openai_key = api_keys.get("openai") or os.environ.get("OPENAI_API_KEY")
    kwargs = {
        "model": os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        "messages": messages,
    }
    if openai_key:
        kwargs["api_key"] = openai_key
    if use_json:
        kwargs["response_format"] = {"type": "json_object"}

    if langfuse_prompt:
        kwargs["langfuse_prompt"] = langfuse_prompt

    response = openai.chat.completions.create(**kwargs)
    return response.choices[0].message.content


# ---------------------------------------------------------------------------
# Plan generator
# ---------------------------------------------------------------------------


@observe(name="generate-plan")
def generate_plan(goal: str, session_id: str) -> list[Task]:
    """
    Ask the LLM to decompose the legal research goal into 3-6 tasks.
    Fetches prompt from Langfuse for centralized management.
    Returns a list of Task objects.
    """
    prompt = langfuse.get_prompt("legal-research/generate-plan", type="chat")
    messages = prompt.compile(goal=goal)
    raw = call_llm(messages, use_json=True, trace_name="generate-plan", langfuse_prompt=prompt)
    data = json.loads(raw)
    return [Task(**t) for t in data["tasks"]]


# ---------------------------------------------------------------------------
# Task executor
# ---------------------------------------------------------------------------


@observe(name="execute-task")
def execute_task(task: Task, state: AgentState) -> Task:
    """
    Execute a single task:
    1. Call search_web with a refined query
    2. Compress raw results to 2-3 sentence summary via LLM
    3. Update task fields (result, sources, reflection, tool_used)
    4. Append compressed summary to state.context_notes
    Raw search results are NEVER stored — only the compressed summary is kept.
    """

    # Step 1 — Build search query from task context + prior notes
    # Validate all variables before passing to prompts
    try:
        context_notes_validated = validate_context_notes(state.context_notes or [])
    except PromptInjectionError as e:
        raise PromptInjectionError(f"Context validation failed: {e}") from e

    context_blob = "\n".join(context_notes_validated) if context_notes_validated else "No prior context."
    refine_prompt = langfuse.get_prompt("legal-research/refine-query", type="chat")
    query_prompt_messages = refine_prompt.compile(
        task_title=task.title,
        task_description=task.description,
        context_notes=context_blob,
    )
    search_query = call_llm(
        query_prompt_messages,
        trace_name="refine-query",
        langfuse_prompt=refine_prompt,
    ).strip()

    # Step 2 — Execute web search
    task.tool_used = "search_web"
    raw_results = search_web(search_query)

    # Build a compact representation of raw content for the compression step
    snippets = []
    sources = []
    for r in raw_results["results"]:
        snippets.append(f"[{r['title']}]: {r['content'][:500]}")
        sources.append(r["url"])

    # Step 3 — Compress raw results (NEVER stored in state)
    compress_prompt = langfuse.get_prompt("legal-research/compress-results", type="chat")
    compression_messages = compress_prompt.compile(
        task_title=task.title,
        search_results="\n\n".join(snippets),
    )
    compressed_summary = call_llm(
        compression_messages,
        trace_name="compress-results",
        langfuse_prompt=compress_prompt,
    )

    # Step 4 — Reflect: did this task answer its goal?
    reflect_prompt = langfuse.get_prompt("legal-research/reflect", type="chat")
    reflection_messages = reflect_prompt.compile(
        task_description=task.description,
        findings=compressed_summary,
    )
    reflection = call_llm(
        reflection_messages,
        trace_name="reflect",
        langfuse_prompt=reflect_prompt,
    )

    # Step 5 — Update task object
    task.result = compressed_summary
    task.sources = sources
    task.reflection = reflection
    task.status = "done"

    # Step 6 — Append ONLY compressed summary to state context (not raw results)
    state.context_notes.append(f"[{task.title}]: {compressed_summary}")

    return task


# ---------------------------------------------------------------------------
# Final report generator
# ---------------------------------------------------------------------------


@observe(name="generate-report")
def generate_final_report(state: AgentState) -> str:
    """
    After all tasks are done, synthesize a comprehensive legal research report.
    Fetches prompt from Langfuse for centralized management.
    Saves it as a markdown file and returns the file path.
    """
    context_blob = "\n\n".join(state.context_notes)
    task_summaries = "\n".join(
        f"- **{t.title}**: {t.result or 'N/A'}" for t in state.tasks
    )
    report_prompt = langfuse.get_prompt("legal-research/generate-report", type="chat")
    messages = report_prompt.compile(
        goal=state.goal,
        task_summaries=task_summaries,
        context_notes=context_blob,
    )
    report_content = call_llm(
        messages,
        trace_name="final-report",
        langfuse_prompt=report_prompt,
    )
    path = save_report(state.session_id, state.goal, report_content)
    return path
