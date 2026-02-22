"""
Run LexAgent evaluation against Langfuse dataset.
Usage: uv run python scripts/run_eval.py

Scores each reflect example using simple JSON parse + status check.
Results are posted back to Langfuse for dashboard tracking.
"""

import json
import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from dotenv import load_dotenv
from langfuse import get_client
from langfuse.openai import openai

# Explicit path so the script works from any working directory
load_dotenv(_REPO_ROOT / ".env", override=True)
langfuse = get_client()

DATASET_NAME = "lexagent-eval-v1"


def score_reflect_output(raw_output: str, expected_status: str) -> float:
    """
    Strict deterministic scorer: 1.0 = correct status, 0.0 = wrong status or invalid JSON.
    Use run_eval_llm_judge.py for semantic partial credit on gap quality.
    """
    try:
        parsed = json.loads(raw_output.strip())
        return 1.0 if parsed.get("status") == expected_status else 0.0
    except Exception:
        return 0.0


def run_reflect_eval(item):
    """Call the reflect prompt and score the result."""
    from app.agent import get_prompt_safe

    prompt = get_prompt_safe("legal-research/reflect", prompt_type="chat")
    messages = prompt.compile(
        task_description=item.input["task_description"],
        findings=item.input["findings"],
    )
    response = openai.chat.completions.create(
        model=os.environ.get("OPENAI_MODEL", "gpt-4.1-mini"),
        messages=messages,
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content
    expected = json.loads(item.expected_output)
    score = score_reflect_output(raw, expected.get("status", ""))
    return raw, score


def main():
    try:
        dataset = langfuse.get_dataset(DATASET_NAME)
    except Exception as e:
        print(f"ERROR: Could not fetch dataset '{DATASET_NAME}': {e}")
        print("Run 'uv run python scripts/create_eval_dataset.py' first to create the dataset.")
        sys.exit(1)
    reflect_items = [i for i in dataset.items if i.metadata.get("prompt") == "legal-research/reflect"]

    print(f"\nRunning eval on {len(reflect_items)} reflect items...")
    scores = []
    for item in reflect_items:
        # Use item.run() so the score is attached to a proper dataset run trace.
        # Do NOT use langfuse.score(trace_id=item.id) — item.id is the dataset item ID, not a trace ID.
        with item.run(
            run_name="reflect-eval-v1",
            run_description="Reflect prompt correctness eval",
        ) as root_span:
            raw, score = run_reflect_eval(item)
            scores.append(score)
            print(f"  {item.metadata.get('name', item.id)}: score={score:.1f} | output={raw[:80]}")
            root_span.score_trace(
                name="reflect-correctness",
                value=score,
                comment=f"Expected: {item.expected_output[:50]}",
            )

    avg = sum(scores) / len(scores) if scores else 0
    print(f"\nAverage reflect correctness: {avg:.2f}")
    if avg < 0.8:
        print("⚠️   Below 0.8 threshold — review reflect prompt in Langfuse")
    else:
        print("✅ Eval passed")


if __name__ == "__main__":
    main()
