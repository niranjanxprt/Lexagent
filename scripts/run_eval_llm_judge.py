"""
Run LexAgent reflect eval with an LLM-as-judge instead of exact status match.
Usage: uv run python scripts/run_eval_llm_judge.py [--judges gpt-4.1,gpt-4.1-mini]

Uses the same dataset (lexagent-eval-v1) and reflect prompt, but scores each
output by asking one or more judge models whether the status and gap are
semantically correct. Results are posted to Langfuse with score names that
match Langfuse score configs (e.g. reflect-llm-judge-gpt-4.1, reflect-llm-judge-gpt-4.1-mini).
Create those configs via Langfuse CLI first: see scripts/run_eval_llm_judge_cli.sh
"""

import argparse
import json
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv
from langfuse import get_client

# Load .env from project root with override so project keys win over stale env (e.g. from Langfuse/uv)
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path, override=True)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY or not OPENAI_API_KEY.strip():
    raise SystemExit(
        "OPENAI_API_KEY is not set. Add it to .env in the project root "
        f"(e.g. {_env_path}) or export it before running."
    )
langfuse = get_client()

DATASET_NAME = "lexagent-eval-v1"
# Default: run both judges. Score names must match score configs created via CLI.
DEFAULT_JUDGES = ["gpt-4.1", "gpt-4.1-mini"]
SCORE_NAME_PREFIX = "reflect-llm-judge-"


def _openai_chat(model: str, messages: list, response_format: dict | None = None) -> str:
    """Call OpenAI Chat API with OPENAI_API_KEY from env (bypasses Langfuse key override)."""
    payload = {
        "model": model,
        "messages": messages,
    }
    if response_format:
        payload["response_format"] = response_format
    with httpx.Client(timeout=60.0) as client:
        r = client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"]


def run_reflect(item):
    """Get reflect prompt output (same as run_eval.py)."""
    from app.agent import get_prompt_safe

    prompt = get_prompt_safe("legal-research/reflect", prompt_type="chat")
    messages = prompt.compile(
        task_description=item.input["task_description"],
        findings=item.input["findings"],
    )
    return _openai_chat(
        os.environ.get("OPENAI_MODEL", "gpt-4.1-mini"),
        messages,
        response_format={"type": "json_object"},
    )


def llm_judge_score(
    task_description: str,
    findings: str,
    expected_output: str,
    actual_output: str,
    judge_model: str,
) -> float:
    """
    Ask judge model to score 0.0–1.0 whether the actual reflect output
    is semantically correct given the expected status/gap.
    """
    try:
        expected = json.loads(expected_output) if isinstance(expected_output, str) else expected_output
    except Exception:
        expected = {"status": "unknown", "gap": ""}

    judge_prompt = f"""You are evaluating a legal research "reflect" step. Given:
- Task: {task_description[:500]}
- Findings: {findings[:800]}
- Expected output (correct): {json.dumps(expected)}
- Actual model output: {actual_output[:500]}

Score from 0.0 to 1.0: 1.0 = status and gap are correct/semantically equivalent; 0.5 = status correct but gap weak or wrong; 0.0 = wrong status or invalid.
Reply with ONLY a single number between 0.0 and 1.0, no explanation."""

    raw = _openai_chat(judge_model, [{"role": "user", "content": judge_prompt}]).strip()
    # Parse first float
    for part in raw.replace(",", " ").split():
        try:
            score = float(part)
            return max(0.0, min(1.0, score))
        except ValueError:
            continue
    return 0.0


def main():
    parser = argparse.ArgumentParser(description="Run reflect eval with LLM-as-judge (GPT-4.1 and/or GPT-4.1-mini)")
    parser.add_argument(
        "--judges",
        type=str,
        default=",".join(DEFAULT_JUDGES),
        help=f"Comma-separated judge model names (default: {','.join(DEFAULT_JUDGES)})",
    )
    parser.add_argument(
        "--scores-json-out",
        type=str,
        default=None,
        metavar="FILE",
        help="Write trace_id and scores to JSON file for curl-based posting (see post_scores_via_curl.sh)",
    )
    args = parser.parse_args()
    judge_models = [m.strip() for m in args.judges.split(",") if m.strip()]

    dataset = langfuse.get_dataset(DATASET_NAME)
    reflect_items = [i for i in dataset.items if i.metadata.get("prompt") == "legal-research/reflect"]

    print(f"\nRunning reflect eval with LLM-as-judge on {len(reflect_items)} items (judges={judge_models})...")
    all_scores: dict[str, list[float]] = {m: [] for m in judge_models}
    scores_for_curl: list[dict] | None = [] if args.scores_json_out else None
    for item in reflect_items:
        expected_out = item.expected_output
        if isinstance(expected_out, dict):
            expected_out = json.dumps(expected_out)
        with item.run(
            run_name="reflect-eval-llm-judge-v1",
            run_description="Reflect correctness via LLM judge (GPT-4.1 + GPT-4.1-mini)",
        ) as root_span:
            raw = run_reflect(item)
            name = item.metadata.get("name", item.id)
            trace_scores: list[dict[str, str | float]] = []
            for judge_model in judge_models:
                score = llm_judge_score(
                    task_description=item.input["task_description"],
                    findings=item.input["findings"],
                    expected_output=expected_out,
                    actual_output=raw,
                    judge_model=judge_model,
                )
                all_scores[judge_model].append(score)
                score_name = f"{SCORE_NAME_PREFIX}{judge_model}"
                if scores_for_curl is None:
                    root_span.score_trace(
                        name=score_name,
                        value=score,
                        comment=f"Expected: {expected_out[:50]}",
                    )
                trace_scores.append({"name": score_name, "value": score})
                print(f"  {name} ({judge_model}): {score:.2f} | output={raw[:50]}...")
            if scores_for_curl is not None:
                scores_for_curl.append({"trace_id": root_span.trace_id, "scores": trace_scores})

    for judge_model in judge_models:
        scores = all_scores[judge_model]
        avg = sum(scores) / len(scores) if scores else 0
        print(f"\nAverage {judge_model}: {avg:.2f}")
        if avg < 0.7:
            print(f"⚠️   {judge_model} below 0.7 — review reflect prompt or expected outputs")
        else:
            print(f"✅ {judge_model} passed")

    if args.scores_json_out and scores_for_curl:
        with open(args.scores_json_out, "w") as f:
            json.dump(scores_for_curl, f, indent=2)
        print(f"\nWrote scores to {args.scores_json_out} for curl-based posting")


if __name__ == "__main__":
    main()
