# CLAUDE.md - Wedding Management Context

CRITICAL: This project follows the rules defined in `AGENTS.MD`. Read that file first to understand the architectural and workflow mandates.

## Build & Test Commands

- **Backend Setup**: `make build` (Docker) or `uv sync` (Local)
- **Run Backend Tests**: `make test` or `pytest backend/apps/`
- **Frontend Setup**: `cd frontend && npm install`
- **Run Frontend Tests**: `cd frontend && npm test`
- **Lint/Format**: `make lint` or `cd backend && ruff check .`
- **Generate API Client**: `make orval` or `cd frontend && npx orval`

## AI Behavior (Claude)

- Be concise and direct.
- Omits greetings and explanations of basic concepts.
- Provide code in Markdown blocks with specified language.
- Prioritize Makefile commands for infrastructure tasks.
