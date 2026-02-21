import json
import os

from langfuse import get_client, observe
from langfuse.openai import openai

from app.context import get_api_keys
from app.models import AgentState, Task
from app.security import (
    PromptInjectionError,
    sanitize_user_input,
    validate_context_notes,
    validate_search_results,
)
from app.tools import save_report, search_web

langfuse = get_client()

# ---------------------------------------------------------------------------
# Inline fallback prompts (used only if Langfuse is unreachable on cold start)
# Keep in sync with Langfuse prompts (production label).
# Author: niranjanxprt
# ---------------------------------------------------------------------------

PROMPT_FALLBACKS: dict[str, list[dict]] = {
    "legal-research/generate-plan": [
        {
            "role": "system",
            "content": (
                "You are a senior legal research assistant. "
                "Decompose the research goal into 3–6 specific research tasks. "
                "All tasks must be research/search tasks — do not include a final "
                "'compile' or 'synthesize' task; report generation is automatic. "
                'Return ONLY valid JSON: {"tasks": [{"title": "...", "description": "..."}, ...]}'
            ),
        },
        {"role": "user", "content": "Legal research goal: {{goal}}"},
    ],
    "legal-research/refine-query": [
        {
            "role": "system",
            "content": (
                "Write a precise web search query (max 12 words) for the given task. "
                "Prefer authoritative sources (eur-lex.europa.eu, gesetze-im-internet.de, "
                "official regulators). Return ONLY the query string — no explanation, no quotes."
            ),
        },
        {
            "role": "user",
            "content": (
                "Task: {{task_title}}\nDescription: {{task_description}}\n"
                "Prior context:\n{{context_notes}}"
            ),
        },
    ],
    "legal-research/compress-results": [
        {
            "role": "system",
            "content": (
                "Compress search results into exactly 2–3 sentences. "
                "Preserve specific article/section references exactly "
                "(e.g. GDPR Article 5, BDSG §26) — do not paraphrase article numbers. "
                "Cite source titles in parentheses."
            ),
        },
        {
            "role": "user",
            "content": "Task: {{task_title}}\n\nSearch results:\n{{search_results}}",
        },
    ],
    "legal-research/reflect": [
        {
            "role": "system",
            "content": (
                "Write exactly one sentence. If the task is fully addressed, say so. "
                "If not, state the main gap in one clause."
            ),
        },
        {"role": "user", "content": "Task: {{task_description}}\n\nFindings: {{findings}}"},
    ],
    "legal-research/generate-report": [
        {
            "role": "system",
            "content": (
                "Write a comprehensive legal research report in Markdown. "
                "Sections: Executive Summary, Key Findings, Legal Implications, "
                "Limitations, Conclusion, Sources (key URLs from research notes). "
                "Where findings reference specific articles, cite them explicitly."
            ),
        },
        {
            "role": "user",
            "content": (
                "Research Goal: {{goal}}\n\nTask Summaries:\n{{task_summaries}}\n\n"
                "Research Notes:\n{{context_notes}}"
            ),
        },
    ],
}


class FallbackPrompt:
    """Mimics the Langfuse prompt interface when Langfuse is unreachable."""

    def __init__(self, messages: list[dict]) -> None:
        self._messages = messages

    def compile(self, **kwargs: str) -> list[dict]:
        result = []
        for msg in self._messages:
            content = msg["content"]
            for key, value in kwargs.items():
                content = content.replace(f"{{{{{key}}}}}", str(value or ""))
            result.append({"role": msg["role"], "content": content})
        return result


def get_prompt_safe(name: str, prompt_type: str = "chat"):
    """
    Fetch prompt from Langfuse, fall back to inline copy on connectivity failure.
    Normal operation: Langfuse SDK cache means zero extra latency.
    Fallback fires only on cold-start connectivity failure — not on cache misses.
    """
    try:
        return langfuse.get_prompt(name, type=prompt_type)
    except Exception:
        return FallbackPrompt(PROMPT_FALLBACKS[name])

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
    # api_key passed per-request (not globally) to support X-OpenAI-API-Key header —
    # lets frontend users supply their own OpenAI key without a shared server-side key.
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
    Decompose the legal research goal into 3–6 research tasks.
    Fetches prompt from Langfuse, falls back to inline copy if unavailable.
    session_id is used for Langfuse trace correlation.
    """
    langfuse.trace(session_id=session_id)
    prompt = get_prompt_safe("legal-research/generate-plan", type="chat")
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
    # Sanitize and validate all variables before passing to prompts
    try:
        task_title_safe = sanitize_user_input(task.title, max_length=500)
        task_description_safe = sanitize_user_input(task.description, max_length=1000)
        context_notes_validated = validate_context_notes(state.context_notes or [])
    except PromptInjectionError as e:
        raise ValueError(f"Invalid input: {e}") from e

    context_blob = "\n".join(context_notes_validated) if context_notes_validated else "No prior context."
    if len(context_blob) > 8000:
        context_blob = "...[earlier context truncated]\n" + context_blob[-7500:]
    refine_prompt = get_prompt_safe("legal-research/refine-query", type="chat")
    query_prompt_messages = refine_prompt.compile(
        task_title=task_title_safe,
        task_description=task_description_safe,
        context_notes=context_blob,
    )
    search_query = call_llm(
        query_prompt_messages,
        trace_name="refine-query",
        langfuse_prompt=refine_prompt,
    ).strip()

    # Step 2 — Execute web search
    task.tool_used = "search_web"
    # TODO: Add exponential backoff retry. Tavily occasionally times out on
    # multi-word legal queries. Documented in Known Limitations.
    raw_results = search_web(search_query)
    raw_results = validate_search_results(raw_results)

    # Build a compact representation of raw content for the compression step
    snippets = []
    sources = []
    for r in raw_results["results"]:
        snippets.append(f"[{r['title']}]: {r['content'][:500]}")
        sources.append(r["url"])

    # Step 3 — Compress raw results (NEVER stored in state).
    # Isolation: compress sees ONLY raw Tavily output, not task goal or prior context,
    # to avoid the model "confirming" findings not present in search results.
    compress_prompt = get_prompt_safe("legal-research/compress-results", type="chat")
    compression_messages = compress_prompt.compile(
        task_title=task_title_safe,
        search_results="\n\n".join(snippets),
    )
    compressed_summary = call_llm(
        compression_messages,
        trace_name="compress-results",
        langfuse_prompt=compress_prompt,
    )

    # Step 4 — Reflect: did this task answer its goal?
    reflect_prompt = get_prompt_safe("legal-research/reflect", type="chat")
    reflection_messages = reflect_prompt.compile(
        task_description=task_description_safe,
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
    if len(context_blob) > 12000:
        context_blob = "...[earlier context truncated]\n" + context_blob[-11000:]
    task_summaries = "\n".join(
        f"- **{t.title}**: {t.result or 'N/A'}" for t in state.tasks
    )
    report_prompt = get_prompt_safe("legal-research/generate-report", type="chat")
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
