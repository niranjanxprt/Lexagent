"""
Security guardrails for LexAgent to prevent prompt injection attacks.
Validates and sanitizes all user inputs before passing to LLM prompts.
"""

import re
from typing import Any


class PromptInjectionError(Exception):
    """Raised when a potential prompt injection is detected."""
    pass


def sanitize_user_input(text: str, max_length: int = 2000) -> str:
    """
    Sanitize user input to prevent prompt injection attacks.

    Checks for:
    - Excessive length (prevents token flooding)
    - Suspicious prompt injection patterns
    - Control characters
    - XML/HTML injection attempts

    Args:
        text: User input to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized text if safe

    Raises:
        PromptInjectionError: If potentially malicious input detected
    """
    if not isinstance(text, str):
        raise PromptInjectionError(f"Input must be string, got {type(text)}")

    # Check length
    if len(text) > max_length:
        raise PromptInjectionError(
            f"Input exceeds maximum length of {max_length} characters. "
            f"Got {len(text)} characters."
        )

    # Check for common prompt injection patterns
    injection_patterns = [
        r"(?i)(ignore|disregard|forget).*?(previous|prior|above).*?(instruction|prompt|message)",
        r"(?i)(system|admin).*?prompt",
        r"(?i)((act|pretend|assume).*?as|role\s*?:|roleplay)",
        r"(?i)(jailbreak|bypass|override|circumvent).*?(rule|filter|restriction|safeguard)",
        r"(?i)(execute|run|eval).*?(code|command|script)",
        r"(?i)(output|show|display).*?(hidden|secret|internal|source)",
        r"(?i)injection|payload|shellcode|reverse.*?shell",
        r"(?i)<\s*(script|iframe|embed|object)",  # HTML/XML injection
        r"(?i)on\w+\s*=",  # Event handler injection
        r"(?i)(;|&&|\|\|)\s*(curl|wget|exec|sh)",  # Command injection
    ]

    for pattern in injection_patterns:
        if re.search(pattern, text):
            raise PromptInjectionError(
                f"Potentially malicious input detected. "
                f"Pattern: {pattern.pattern if hasattr(pattern, 'pattern') else pattern}"
            )

    # Check for excessive control characters
    control_char_count = sum(1 for c in text if ord(c) < 32 and c not in '\n\t\r')
    if control_char_count > 5:
        raise PromptInjectionError(
            f"Excessive control characters detected ({control_char_count})"
        )

    # Check for null bytes
    if '\x00' in text:
        raise PromptInjectionError("Null bytes detected in input")

    return text


def validate_goal(goal: str) -> str:
    """
    Validate and sanitize the research goal.

    Args:
        goal: Research goal from user

    Returns:
        Sanitized goal

    Raises:
        PromptInjectionError: If goal is malicious
    """
    if not goal or not goal.strip():
        raise PromptInjectionError("Research goal cannot be empty")

    return sanitize_user_input(goal, max_length=500)


def validate_task_description(description: str) -> str:
    """
    Validate and sanitize task description.

    Args:
        description: Task description

    Returns:
        Sanitized description

    Raises:
        PromptInjectionError: If description is malicious
    """
    if not description or not description.strip():
        raise PromptInjectionError("Task description cannot be empty")

    return sanitize_user_input(description, max_length=1000)


def validate_context_notes(notes: list[str]) -> list[str]:
    """
    Validate and sanitize accumulated context notes.

    Args:
        notes: List of context notes from previous tasks

    Returns:
        Sanitized list of notes

    Raises:
        PromptInjectionError: If any note is malicious
    """
    if not isinstance(notes, list):
        raise PromptInjectionError("Context notes must be a list")

    sanitized = []
    for note in notes:
        if not isinstance(note, str):
            raise PromptInjectionError(f"Context note must be string, got {type(note)}")
        sanitized.append(sanitize_user_input(note, max_length=2000))

    return sanitized


def validate_search_results(results: dict) -> dict:
    """
    Validate and sanitize search results from Tavily.

    Args:
        results: Search results dictionary

    Returns:
        Sanitized results

    Raises:
        PromptInjectionError: If results contain malicious content
    """
    if not isinstance(results, dict):
        raise PromptInjectionError("Search results must be a dictionary")

    if "results" not in results:
        raise PromptInjectionError("Search results missing 'results' key")

    if not isinstance(results["results"], list):
        raise PromptInjectionError("Search results['results'] must be a list")

    sanitized_results = []
    for item in results["results"]:
        if not isinstance(item, dict):
            raise PromptInjectionError("Each search result must be a dictionary")

        # Validate required fields
        if not all(key in item for key in ["title", "url", "content"]):
            raise PromptInjectionError("Search result missing required fields")

        # Sanitize content, but allow URLs (they're from Tavily)
        sanitized_item = {
            "title": sanitize_user_input(item["title"], max_length=500),
            "url": item["url"],  # URL from Tavily is trusted
            "content": sanitize_user_input(item["content"], max_length=5000),
        }
        sanitized_results.append(sanitized_item)

    return {"results": sanitized_results}


def validate_all_variables(
    goal: str | None = None,
    task_title: str | None = None,
    task_description: str | None = None,
    context_notes: list[str] | None = None,
    search_results: dict | None = None,
    findings: str | None = None,
    task_summaries: str | None = None,
) -> dict[str, Any]:
    """
    Validate all prompt variables in one call.

    Args:
        goal: Research goal
        task_title: Task title
        task_description: Task description
        context_notes: List of context notes
        search_results: Search results from Tavily
        findings: Compressed findings
        task_summaries: Task summaries for report

    Returns:
        Dictionary of validated variables

    Raises:
        PromptInjectionError: If any variable is malicious
    """
    validated = {}

    if goal is not None:
        validated["goal"] = validate_goal(goal)

    if task_title is not None:
        validated["task_title"] = sanitize_user_input(task_title, max_length=500)

    if task_description is not None:
        validated["task_description"] = validate_task_description(task_description)

    if context_notes is not None:
        validated["context_notes"] = validate_context_notes(context_notes)

    if search_results is not None:
        validated["search_results"] = validate_search_results(search_results)

    if findings is not None:
        validated["findings"] = sanitize_user_input(findings, max_length=2000)

    if task_summaries is not None:
        validated["task_summaries"] = sanitize_user_input(task_summaries, max_length=5000)

    return validated
