#!/usr/bin/env bash
# Update Langfuse prompts (creates new versions with Block D content).
# Uses the Python init script (reliable for chat prompts). Requires .env with Langfuse keys.
# Run from repo root: bash scripts/update_langfuse_prompts_cli.sh

set -e
cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
  echo "Missing .env. Copy .env.example and set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY."
  exit 1
fi

echo "Updating Langfuse prompts (Block D content)..."
if command -v uv &>/dev/null; then
  uv run python app/init_langfuse_prompts.py
else
  python app/init_langfuse_prompts.py
fi
echo "Done. New versions have the 'production' label. List prompts: npx langfuse-cli --env .env api prompts list"
