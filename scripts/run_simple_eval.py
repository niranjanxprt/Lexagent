#!/usr/bin/env python3
"""
Simple eval: run a small dataset of goals through the agent and optionally check reports.

No server or Langfuse traces required. Uses .env for OPENAI and TAVILY.
Writes reports to reports/ with session_id like eval-<id>-<short_uuid>.

Usage:
  uv run python scripts/run_simple_eval.py
  uv run python scripts/run_simple_eval.py --limit 1
  uv run python scripts/run_simple_eval.py --no-check   # skip keyword check, just run and save reports
"""

import argparse
import json
import os
import sys
import uuid
from pathlib import Path

# Repo root
REPO_ROOT = Path(__file__).resolve().parent.parent
DATASET_PATH = Path(__file__).resolve().parent / "eval_dataset.json"


def load_dataset(limit: int | None) -> list[dict]:
    """Load eval_dataset.json and optionally limit number of items."""
    if not DATASET_PATH.exists():
        print(f"Dataset not found: {DATASET_PATH}", file=sys.stderr)
        sys.exit(1)
    with open(DATASET_PATH, encoding="utf-8") as f:
        items = json.load(f)
    if limit is not None:
        items = items[:limit]
    return items


def run_agent_for_goal(goal: str, session_id: str) -> str | None:
    """Run plan → execute all tasks → generate report. Returns report path or None on failure."""
    from app.agent import generate_plan, execute_task, generate_final_report
    from app.models import AgentState
    from app.storage import save_session

    state = AgentState(goal=goal, session_id=session_id)
    state.mode = "plan"
    try:
        tasks = generate_plan(goal, session_id)
    except Exception as e:
        print(f"  generate_plan failed: {e}", file=sys.stderr)
        return None
    state.tasks = tasks
    state.mode = "execute"
    save_session(state)

    while True:
        pending = [t for t in state.tasks if t.status == "pending"]
        if not pending:
            break
        task = pending[0]
        try:
            execute_task(task, state)
        except Exception as e:
            print(f"  execute_task failed: {e}", file=sys.stderr)
            return None
        save_session(state)

    try:
        report_path = generate_final_report(state)
    except Exception as e:
        print(f"  generate_final_report failed: {e}", file=sys.stderr)
        return None
    state.final_report_path = report_path
    state.is_active = False
    state.mode = "done"
    save_session(state)
    return report_path


def check_report(path: Path, expected_keywords: list[str]) -> tuple[bool, list[str]]:
    """Return (all_found, missing_keywords)."""
    if not path.exists():
        return False, list(expected_keywords)
    text = path.read_text(encoding="utf-8").lower()
    missing = [k for k in expected_keywords if k.lower() not in text]
    return len(missing) == 0, missing


def main():
    parser = argparse.ArgumentParser(
        description="Run simple eval on eval_dataset.json"
    )
    parser.add_argument("--limit", type=int, default=None, help="Run only first N items (e.g. 1 for a quick test)")
    parser.add_argument("--no-check", action="store_true", help="Do not check reports for expected keywords")
    args = parser.parse_args()

    sys.path.insert(0, str(REPO_ROOT))
    os.environ.setdefault("LEXAGENT_DATA_DIR", str(REPO_ROOT / "data"))
    os.environ.setdefault("LEXAGENT_REPORTS_DIR", str(REPO_ROOT / "reports"))

    items = load_dataset(args.limit)
    print(f"Running eval on {len(items)} item(s) from {DATASET_PATH.name}\n")

    results = []
    for i, item in enumerate(items, 1):
        goal = item["goal"]
        id_ = item.get("id", f"item-{i}")
        short_uid = uuid.uuid4().hex[:8]
        session_id = f"eval-{id_}-{short_uid}"
        print(f"[{i}/{len(items)}] {id_} ... ", end="", flush=True)

        report_path = run_agent_for_goal(goal, session_id)
        if report_path is None:
            print("FAIL (run error)")
            results.append({"id": id_, "pass": False, "path": None, "note": "run error"})
            continue

        path = Path(report_path)
        if args.no_check:
            print(f"OK -> {path}")
            results.append({"id": id_, "pass": True, "path": str(path)})
            continue

        expected = item.get("expected_keywords") or []
        if not expected:
            print(f"OK (no checklist) -> {path}")
            results.append({"id": id_, "pass": True, "path": str(path)})
            continue

        ok, missing = check_report(path, expected)
        if ok:
            print(f"PASS -> {path}")
            results.append({"id": id_, "pass": True, "path": str(path)})
        else:
            print(f"FAIL (missing: {missing}) -> {path}")
            results.append({"id": id_, "pass": False, "path": str(path), "missing": missing})

    passed = sum(1 for r in results if r["pass"])
    print(f"\n--- Summary: {passed}/{len(results)} passed ---")
    print("Reports:", [r["path"] for r in results if r.get("path")])
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
