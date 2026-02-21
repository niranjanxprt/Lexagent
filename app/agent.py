import logging
import os
from typing import TypeVar

from langfuse import get_client, observe, propagate_attributes
from langfuse.openai import openai
from pydantic import BaseModel, ValidationError

from app.models import AgentState, ReflectResult, ResearchPlan, Task

logger = logging.getLogger(__name__)
from app.security import (
    validate_search_results,
)
from app.tools import save_report, search_web

# Initialize Langfuse with graceful fallback if credentials are missing
try:
    langfuse = get_client()
except Exception:
    # Langfuse is optional; falls back to inline prompts
    langfuse = None

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
                "You're a senior legal research assistant breaking down a research goal into 3–6 concrete tasks. "
                "Each task should be a research/search task. Do not add a final 'compile' or 'synthesize' task — report generation is automatic. "
                'Return ONLY valid JSON: {"tasks": [{"title": "...", "description": "..."}, ...]}'
            ),
        },
        {"role": "user", "content": "Legal research goal: {{goal}}"},
    ],
    "legal-research/refine-query": [
        {
            "role": "system",
            "content": (
                "Turn the task into one short web search query (max 12 words). Prefer wording that hits authoritative sources. "
                "Reply with only the query: no explanation, no quotes. Do not add preamble like 'Here is the query'."
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
                "Summarize the search results in 2–3 sentences. Keep article/section refs exact (e.g. GDPR Article 5, BDSG §26); do not paraphrase. "
                "Cite source in parentheses. Do not add content that wasn't in the results."
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
                "Check whether the findings fully answer the task. Return ONLY valid JSON, no markdown or prose. "
                'Schema: {"status":"fully_addressed"|"partially_addressed"|"not_addressed","gap":"..."} '
                'Use "fully_addressed" only when the core legal question is answered with source-backed support. '
                'Otherwise set "gap" to the single most important missing element (max 20 words). Set "gap" to "" when fully_addressed.'
            ),
        },
        {"role": "user", "content": "Task: {{task_description}}\n\nFindings: {{findings}}"},
    ],
    "legal-research/generate-report": [
        {
            "role": "system",
            "content": (
                "Draft a legal research report in Markdown: Executive Summary, Key Findings, Legal Implications, Limitations, Conclusion, Sources (key URLs). "
                "Cite articles explicitly where relevant. Do not invent articles or sources not in the notes."
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

    is_fallback = True  # Langfuse OpenAI wrapper checks this to skip prompt linking

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


def _full_model() -> str:
    """
    Full (non-mini) model for high-stakes steps: generate-plan and generate-report.
    Derived from OPENAI_MODEL; no extra env vars. Examples: gpt-4.1-mini -> gpt-4.1.
    """
    base = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    return base.replace("-mini", "").replace("-nano", "").strip() or base


# ---------------------------------------------------------------------------
# LLM wrapper
# ---------------------------------------------------------------------------

T = TypeVar("T", bound=BaseModel)


@observe(name="call-llm", as_type="generation")
def call_llm(
    messages: list,
    use_json: bool = False,
    trace_name: str | None = None,
    langfuse_prompt=None,
    model: str | None = None,
) -> str:
    """
    Wrapper around OpenAI chat completions.
    Langfuse @observe() automatically captures input, output, token usage, latency.
    model: overrides OPENAI_MODEL when set (e.g. _full_model() for plan/report).
    """
    kwargs = {
        "model": model or os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        "messages": messages,
    }
    if use_json:
        kwargs["response_format"] = {"type": "json_object"}
    if langfuse_prompt:
        kwargs["langfuse_prompt"] = langfuse_prompt
    response = openai.chat.completions.create(**kwargs)
    return response.choices[0].message.content


def call_llm_validated(
    messages: list,
    model_class: type[T],
    call_kwargs: dict | None = None,
    max_retries: int = 1,
) -> T:
    """
    Call LLM, parse JSON, validate with Pydantic. Retry once with correction on parse/validation failure.
    Use for ResearchPlan and ReflectResult.
    """
    call_kwargs = call_kwargs or {}
    for attempt in range(max_retries + 1):
        raw = call_llm(messages, **call_kwargs)
        try:
            return model_class.model_validate_json(raw)
        except (ValueError, ValidationError) as e:
            if attempt < max_retries:
                messages = messages + [
                    {"role": "assistant", "content": raw},
                    {
                        "role": "user",
                        "content": (
                            f"Your output failed validation: {e}. "
                            f"Return ONLY valid JSON matching this schema: "
                            f"{model_class.model_json_schema()}. No other text."
                        ),
                    },
                ]
            else:
                raise ValueError(
                    f"{model_class.__name__} validation failed after {max_retries + 1} attempts. "
                    f"Last raw output: {raw[:200]}"
                ) from e


# ---------------------------------------------------------------------------
# Plan generator
# ---------------------------------------------------------------------------


@observe(name="generate-plan")
def generate_plan(goal: str, session_id: str) -> list[Task]:
    """
    Decompose the legal research goal into 3–6 research tasks.
    Uses full model (non-mini) for plan quality; validated via ResearchPlan.
    """
    with propagate_attributes(session_id=session_id):
        prompt = get_prompt_safe("legal-research/generate-plan", prompt_type="chat")
        messages = prompt.compile(goal=goal)
        plan = call_llm_validated(
            messages,
            ResearchPlan,
            {"use_json": True, "trace_name": "generate-plan", "langfuse_prompt": prompt, "model": _full_model()},
        )
        return [Task(title=t.title, description=t.description) for t in plan.tasks]


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
    # Note: task.title, task.description, and context_notes are LLM-generated,
    # so they are not validated against injection patterns (only user input at API boundary is validated).
    task_title_safe = task.title
    task_description_safe = task.description
    context_notes_list = state.context_notes or []

    context_blob = "\n".join(context_notes_list) if context_notes_list else "No prior context."
    if len(context_blob) > 8000:
        context_blob = "...[earlier context truncated]\n" + context_blob[-7500:]
    refine_prompt = get_prompt_safe("legal-research/refine-query", prompt_type="chat")
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
    compress_prompt = get_prompt_safe("legal-research/compress-results", prompt_type="chat")
    compression_messages = compress_prompt.compile(
        task_title=task_title_safe,
        search_results="\n\n".join(snippets),
    )
    compressed_summary = call_llm(
        compression_messages,
        trace_name="compress-results",
        langfuse_prompt=compress_prompt,
    )

    # Step 4 — Reflect: validated JSON (status + gap)
    reflect_prompt = get_prompt_safe("legal-research/reflect", prompt_type="chat")
    reflection_messages = reflect_prompt.compile(
        task_description=task_description_safe,
        findings=compressed_summary,
    )
    reflect_result = call_llm_validated(
        reflection_messages,
        ReflectResult,
        {"use_json": True, "trace_name": "reflect", "langfuse_prompt": reflect_prompt},
    )
    task.reflection = reflect_result.gap.strip() or "Fully addressed."
    task.reflect_status = reflect_result.status
    if reflect_result.status != "fully_addressed":
        logger.warning(
            "task_incomplete",
            extra={"task": task.title, "status": reflect_result.status, "gap": reflect_result.gap},
        )

    # Step 5 — Update task object
    task.result = compressed_summary
    task.sources = sources
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
    report_prompt = get_prompt_safe("legal-research/generate-report", prompt_type="chat")
    messages = report_prompt.compile(
        goal=state.goal,
        task_summaries=task_summaries,
        context_notes=context_blob,
    )
    report_content = call_llm(
        messages,
        trace_name="final-report",
        langfuse_prompt=report_prompt,
        model=_full_model(),
    )
    path = save_report(state.session_id, state.goal, report_content)
    return path
