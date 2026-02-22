#!/bin/bash
# Pre-merge verification: tests, lint, Docker build and run (same image as Railway).
# Run from repo root: bash scripts/verify_before_merge.sh
set -e

echo "=== LexAgent Pre-Merge Verification ==="
echo ""

# 1. Unit tests
echo "1. Running Python tests..."
make test
echo "   ✓ Python tests passed"
echo ""

# 2. Lint
echo "2. Running linter..."
make lint
echo "   ✓ Lint passed"
echo ""

# 3. React tests
echo "3. Running React tests..."
make react-test
echo "   ✓ React tests passed"
echo ""

# 4. Docker build (same as Railway)
echo "4. Building Docker image (Railway-equivalent)..."
docker build -t lexagent-verify .
echo "   ✓ Docker build passed"
echo ""

# 5. Run single container (same as Railway)
echo "5. Starting container..."
docker rm -f lexagent-verify 2>/dev/null || true
if [[ ! -f .env ]]; then
  echo "   ⚠ .env not found; starting with minimal env (health check only)"
  docker run -d -p 8000:8000 --name lexagent-verify -e OPENAI_API_KEY= -e TAVILY_API_KEY= lexagent-verify
else
  docker run -d -p 8000:8000 --env-file .env --name lexagent-verify lexagent-verify
fi
echo "   Waiting for server..."
sleep 5

# 6. Health check
echo "6. Verifying endpoints..."
HEALTH=$(curl -s http://localhost:8000/health)
if [[ "$HEALTH" == *"ok"* ]]; then
  echo "   ✓ /health OK"
else
  echo "   ✗ /health failed: $HEALTH"
  docker rm -f lexagent-verify 2>/dev/null || true
  exit 1
fi

# 7. React at /
ROOT_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/)
if [[ "$ROOT_STATUS" == "200" ]]; then
  echo "   ✓ / (React app) OK"
else
  echo "   ✗ / returned $ROOT_STATUS"
  docker rm -f lexagent-verify 2>/dev/null || true
  exit 1
fi

echo ""
echo "=== All checks passed! Safe to merge dev → main ==="
echo ""
echo "Railway uses the same Dockerfile. Backend serves React at / and API at /agent/*."
echo ""

docker rm -f lexagent-verify 2>/dev/null || true
echo "Container stopped."
