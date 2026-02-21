#!/usr/bin/env bash
# Add Railway volume and optional env vars via CLI.
# Requires: railway login, and project linked (railway link or run from linked dir).
# Run from repo root: bash scripts/railway_setup_volume_and_vars.sh

set -e
cd "$(dirname "$0")/.."

echo "Railway: adding volume at /app/data (sessions persistence)..."
railway volume add --mount-path /app/data

echo ""
echo "Optional: set OPENAI_MODEL to gpt-4o for stronger legal reasoning:"
echo "  railway variables --set OPENAI_MODEL=gpt-4o"
echo ""
echo "Optional: add volume for reports:"
echo "  railway volume add --mount-path /app/reports"
echo ""
echo "List volumes: railway volume list"
echo "List variables: railway variables"
