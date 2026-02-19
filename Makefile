.PHONY: help install setup backend frontend dev lint lint-fix test clean logs kill react-install react react-build

help:
	@echo "LexAgent - Makefile Commands"
	@echo "============================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install        Install dependencies with UV"
	@echo "  make react-install  Install React frontend dependencies"
	@echo "  make setup          Copy .env.example to .env"
	@echo ""
	@echo "Running:"
	@echo "  make backend        Start FastAPI backend on port 8000"
	@echo "  make frontend       Start Streamlit UI on port 8501"
	@echo "  make react          Start React frontend on port 5173"
	@echo "  make dev            Run backend + Streamlit frontend together"
	@echo ""
	@echo "Development:"
	@echo "  make lint           Run Ruff linter"
	@echo "  make lint-fix       Auto-fix linting issues"
		@echo "  make test           Run Python backend tests"
	@echo "  make react-test     Run React frontend tests"
	@echo "  make test-all       Run all tests"
	@echo ""
	@echo "Build:"
	@echo "  make react-build    Build React frontend for production"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean          Remove session data and reports"
	@echo "  make logs           Show backend logs"
	@echo "  make kill           Kill backend/frontend processes"
	@echo ""

install:
	uv sync

setup:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ Created .env - please add your API keys"; \
	else \
		echo "⚠️  .env already exists"; \
	fi

backend:
	@echo "Starting FastAPI backend on port 8000..."
	@echo "API Docs: http://localhost:8000/docs"
	uv run uvicorn app.main:app --port 8000 --reload

frontend:
	@echo "Starting Streamlit UI on port 8501..."
	@echo "UI: http://localhost:8501"
	uv run streamlit run frontend/ui.py

dev:
	@echo "Starting LexAgent (Backend + Frontend)..."
	@echo ""
	@echo "Backend:  http://localhost:8000"
	@echo "Frontend: http://localhost:8501"
	@echo "Docs:     http://localhost:8000/docs"
	@echo ""
	uv run uvicorn app.main:app --port 8000 > /tmp/backend.log 2>&1 &
	@sleep 6
	uv run streamlit run frontend/ui.py --server.port 8501 &
	@echo "Both services started! Press Ctrl+C to stop."

lint:
	@echo "Running Ruff linter..."
	uv run ruff check app/ frontend/

lint-fix:
	@echo "Auto-fixing with Ruff..."
	uv run ruff check --fix app/ frontend/

test:
	@echo "Running Python backend tests (no API keys needed)..."
	@echo ""
	uv run python -c "from app.models import Task, AgentState; from app.storage import save_session, load_session; task = Task(title='Test', description='Test'); state = AgentState(goal='Test', tasks=[task]); save_session(state); loaded = load_session(state.session_id); assert loaded.goal == state.goal; print('✅ All core tests passed!')"

react-test:
	@echo "Running React frontend tests..."
	cd frontend-react && npm test -- --run

test-all: test react-test
	@echo ""
	@echo "✅ All tests passed (Python + React)"

clean:
	@echo "Cleaning up session data and reports..."
	rm -rf data/*.json reports/*.md 2>/dev/null || true
	@echo "✅ Cleaned"

logs:
	@echo "Backend logs:"
	@tail -20 /tmp/backend.log 2>/dev/null || echo "No logs found"

kill:
	@echo "Killing processes..."
	@pkill -f "uvicorn" 2>/dev/null || true
	@pkill -f "streamlit" 2>/dev/null || true
	@pkill -f "vite" 2>/dev/null || true
	@echo "✅ Done"

react-install:
	@echo "Installing React frontend dependencies..."
	cd frontend-react && npm install

react:
	@echo "Starting React frontend on port 5173..."
	@echo "UI: http://localhost:5173"
	cd frontend-react && npm run dev

react-build:
	@echo "Building React frontend for production..."
	cd frontend-react && npm run build

.DEFAULT_GOAL := help
