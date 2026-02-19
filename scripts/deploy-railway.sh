#!/bin/bash
# Deploy LexAgent to Railway via CLI
# Run this AFTER: railway login (in your terminal)

set -e
cd "$(dirname "$0")/.."

echo "=== LexAgent Railway Deployment ==="

# 1. Link or create project
if ! railway status 2>/dev/null; then
  echo "Linking project..."
  railway init
fi

# 2. Set variables (use your own keys)
if [ -n "$OPENAI_API_KEY" ]; then
  railway variables set OPENAI_API_KEY="$OPENAI_API_KEY"
fi
if [ -n "$TAVILY_API_KEY" ]; then
  railway variables set TAVILY_API_KEY="$TAVILY_API_KEY"
fi

# 3. Deploy
echo "Deploying..."
railway up

# 4. Generate domain if needed
echo ""
echo "To generate a public domain, run: railway domain"
echo "Then test: curl https://YOUR-DOMAIN/health"
