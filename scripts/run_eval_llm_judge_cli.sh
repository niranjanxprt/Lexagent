#!/usr/bin/env bash
# LLM-as-a-Judge eval using Langfuse CLI + Python + curl.
# 1) Langfuse CLI: create score configs, list dataset.
# 2) Python: run reflect eval (creates dataset run + traces).
# 3) Scores: via SDK (default) or via curl (--scores-via-curl).
#
# Prereqs: .env with LANGFUSE_*, OPENAI_API_KEY; dataset lexagent-eval-v1 with 4 items.
# Usage: ./scripts/run_eval_llm_judge_cli.sh [--scores-via-curl]

set -e
cd "$(dirname "$0")/.."

SCORES_VIA_CURL=false
[[ "${1:-}" == "--scores-via-curl" ]] && SCORES_VIA_CURL=true

echo "=== 1. Langfuse CLI: list dataset (confirm 4 items) ==="
npx langfuse-cli --env .env api dataset-items list --dataset-name lexagent-eval-v1

echo ""
echo "=== 2. Langfuse CLI: create score configs for LLM-as-a-Judge (ignore if already exist) ==="
npx langfuse-cli --env .env api score-configs create \
  --name "reflect-llm-judge-gpt-4.1" \
  --dataType NUMERIC \
  --minValue 0 \
  --maxValue 1 \
  --description "LLM-as-judge score (0-1) for reflect step using GPT-4.1" \
  || true
npx langfuse-cli --env .env api score-configs create \
  --name "reflect-llm-judge-gpt-4.1-mini" \
  --dataType NUMERIC \
  --minValue 0 \
  --maxValue 1 \
  --description "LLM-as-judge score (0-1) for reflect step using GPT-4.1-mini" \
  || true

echo ""
echo "=== 3. Run reflect eval with both judges (GPT-4.1 + GPT-4.1-mini) ==="
if $SCORES_VIA_CURL; then
  SCORES_JSON=$(mktemp)
  trap "rm -f $SCORES_JSON" EXIT
  PYTHONPATH=. uv run python scripts/run_eval_llm_judge.py --judges "gpt-4.1,gpt-4.1-mini" --scores-json-out "$SCORES_JSON"
  echo ""
  echo "=== 4. Post scores via curl (Langfuse REST API) ==="
  ./scripts/post_scores_via_curl.sh "$SCORES_JSON"
else
  PYTHONPATH=. uv run python scripts/run_eval_llm_judge.py --judges "gpt-4.1,gpt-4.1-mini"
fi

echo ""
echo "=== 5. Langfuse CLI: list dataset runs ==="
npx langfuse-cli --env .env api datasets get-get-runs lexagent-eval-v1 --limit 3
