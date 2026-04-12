# GEMINI.md - Wedding Management Context

CRITICAL: This project follows the rules defined in `ENGINEERING.md`. Read that file first to understand the architectural and workflow mandates.

## Build & Test Commands

- **Backend Setup**: `make build` (Docker) or `uv sync` (Local)
- **Run Backend Tests**: `make test` or `pytest backend/apps/`
- **Frontend Setup**: `cd frontend && npm install`
- **Run Frontend Tests**: `cd frontend && npm test`
- **Lint/Format**: `make lint` or `cd backend && ruff check .`
- **Generate API Client**: `make orval` or `cd frontend && npx orval`

## AI Behavior (Gemini)

- Adopt a professional, direct, and concise tone (minimal filler).
- Use `run_shell_command` with an explanation for modifying tasks.
- Prioritize **Research -> Strategy -> Execution** lifecycle.
- Never compromise on idiomatic quality or type safety (TypeScript/Zod).
- Follow Conventional Commits strictly.
- Always check `ENGINEERING.md` before making architectural decisions.
