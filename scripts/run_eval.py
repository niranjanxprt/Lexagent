"""
Run LexAgent evaluation against Langfuse dataset.
Usage: uv run python scripts/run_eval.py

Scores each reflect example using simple JSON parse + status check.
Results are posted back to Langfuse for dashboard tracking.
"""

import json
import os

from dotenv import load_dotenv
from langfuse import get_client
from langfuse.openai import openai

load_dotenv()
langfuse = get_client()

DATASET_NAME = "lexagent-eval-v1"


def score_reflect_output(raw_output: str, expected_status: str) -> float:
    """Returns 1.0 if valid JSON with correct status, 0.5 if valid JSON wrong status, 0.0 if invalid."""
    try:
        parsed = json.loads(raw_output.strip())
        if parsed.get("status") == expected_status:
            return 1.0
        return 0.5  # valid JSON but wrong status
    except Exception:
        return 0.0  # invalid JSON


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
    dataset = langfuse.get_dataset(DATASET_NAME)
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
