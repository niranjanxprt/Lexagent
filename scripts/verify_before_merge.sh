#!/bin/bash
# Pre-merge verification: ensures Docker + React work before merging dev to main.
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
docker compose build backend
echo "   ✓ Docker build passed"
echo ""

# 5. Full stack test
echo "5. Starting Docker Compose (backend + react)..."
docker compose down 2>/dev/null || true
docker compose up -d
echo "   Waiting for services..."
sleep 5

# 6. Health check
echo "6. Verifying endpoints..."
HEALTH=$(curl -s http://localhost:8000/health)
if [[ "$HEALTH" == *"ok"* ]]; then
  echo "   ✓ /health OK"
else
  echo "   ✗ /health failed: $HEALTH"
  docker compose down
  exit 1
fi

# 7. React at /
ROOT_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/)
if [[ "$ROOT_STATUS" == "200" ]]; then
  echo "   ✓ / (React app) OK"
else
  echo "   ✗ / returned $ROOT_STATUS"
  docker compose down
  exit 1
fi

# 8. React container (optional)
REACT_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/ 2>/dev/null || echo "000")
if [[ "$REACT_STATUS" == "200" ]]; then
  echo "   ✓ React dev container OK"
else
  echo "   ⚠ React container not reachable (optional for Railway)"
fi

echo ""
echo "=== All checks passed! Safe to merge dev → main ==="
echo ""
echo "Railway note: Main branch uses the same Dockerfile. No Streamlit;"
echo "backend serves React at / and API at /agent/*. Deployment unchanged."
echo ""

docker compose down
echo "Containers stopped."
