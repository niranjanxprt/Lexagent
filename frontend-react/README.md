# LexAgent React Frontend

React + TypeScript frontend for LexAgent. Provides a modern, responsive interface for the legal research AI agent.

## Features

- Session management (create, browse, switch)
- Real-time task progress and findings
- Report download and markdown preview
- Auto-run for batch execution
- LocalStorage persistence for last session

## Tech Stack

- React 18, TypeScript, Vite
- Tailwind CSS, Lucide React
- React Markdown (GFM support)

## Quick Start

```bash
npm install
npm run dev
```

Open http://localhost:5173 (or next available port).

Ensure the backend is running on port 8000. Set `VITE_API_URL` in `.env` if different.

## Commands

| Command | Description |
|---------|-------------|
| `npm run dev` | Start dev server |
| `npm run build` | Production build |
| `npm run preview` | Preview production build |
| `npm test` | Run Vitest tests |
| `npm run lint` | TypeScript check |

## Project Structure

```
src/
├── components/       # UI components
│   ├── Sidebar.tsx
│   ├── NewSession.tsx
│   ├── SessionView.tsx
│   ├── TaskCard.tsx
│   ├── FinalReport.tsx
│   └── ExecutionControls.tsx
├── lib/api.ts        # API client
├── types/index.ts    # TypeScript types
├── utils/format.ts   # Formatting helpers
└── test/             # Vitest tests
```

## API Endpoints Used

- `GET /sessions` — List sessions
- `GET /agent/{id}` — Get session state
- `POST /agent/start` — Start session
- `POST /agent/{id}/execute` — Execute next step
- `GET /agent/{id}/report` — Get report markdown
- `DELETE /agent/{id}` — Delete session

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `http://localhost:8000` | Backend API URL |
