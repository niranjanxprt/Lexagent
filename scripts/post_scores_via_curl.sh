#!/usr/bin/env bash
# Post scores to Langfuse via REST API (curl) when Langfuse CLI lacks --value for scores create.
# Usage:
#   1. Run eval with --scores-json-out to generate scores file:
#      PYTHONPATH=. uv run python scripts/run_eval_llm_judge.py --scores-json-out /tmp/scores.json
#   2. Post scores via this script:
#      ./scripts/post_scores_via_curl.sh /tmp/scores.json
#
# Prereqs: .env with LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_BASE_URL (optional)

set -e
SCORES_JSON="${1:?Usage: $0 <scores.json>}"
cd "$(dirname "$0")/.."

# Load .env (simple export; use .env in project root)
if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  . .env
  set +a
fi

LANGFUSE_BASE_URL="${LANGFUSE_BASE_URL:-https://cloud.langfuse.com}"
AUTH=$(echo -n "${LANGFUSE_PUBLIC_KEY}:${LANGFUSE_SECRET_KEY}" | base64)

echo "Posting scores from $SCORES_JSON to Langfuse..."
count=0
while IFS= read -r line; do
  trace_id=$(echo "$line" | jq -r '.trace_id')
  while IFS= read -r score; do
    name=$(echo "$score" | jq -r '.name')
    value=$(echo "$score" | jq -r '.value')
    curl -s -X POST "${LANGFUSE_BASE_URL}/api/public/scores" \
      -H "Authorization: Basic $AUTH" \
      -H "Content-Type: application/json" \
      -d "{\"traceId\":\"$trace_id\",\"name\":\"$name\",\"value\":$value}" > /dev/null
    echo "  Posted $name=$value to trace $trace_id"
    count=$((count + 1))
  done < <(echo "$line" | jq -c '.scores[]')
done < <(jq -c '.[]' "$SCORES_JSON")
echo "Posted $count scores."
