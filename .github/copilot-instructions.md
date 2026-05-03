# GitHub Copilot Custom Instructions - Wedding Management

This file provides repository-specific guidance to GitHub Copilot for the Wedding Management System.

## 🚀 Project Overview
A complete wedding management system with a modern **React SPA + Django Ninja API** architecture.
- **Backend**: Python 3.12+, Django, Django Ninja. Organized by business domains.
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS, shadcn/ui.
- **Contract-Driven**: API client and MSW mocks are generated via Orval from `openapi.json`.

## 🏗 Architectural Mandates (Strict)

### Backend (apps/)
- **Service Layer**: API endpoints in `api.py` MUST ONLY delegate to functions in `services.py`.
- **Multi-tenancy**: Every service function MUST receive `company` and use `Model.objects.for_tenant(company)` for explicit data filtering.
- **Data Integrity**: Models must inherit from `BaseModel` (triggers `full_clean()` on `save()`).
- **Typing**: Strict type hinting is required. `mypy` must pass.

### Frontend (src/)
- **Feature-Based**: Organize code in `src/features/<feature_name>/` (components, hooks, pages, types).
- **No Manual Fetch**: It is FORBIDDEN to use `fetch` or `axios` directly. Use only Orval-generated hooks in `src/api/generated/`.
- **UI Components**: Use **shadcn/ui** (in `src/components/ui/`). Prioritize composition over direct modification.
- **Icons**: Use exclusively `lucide-react`.
- **Forms**: Use `react-hook-form` + `zod` validation.

## 🧪 Testing Standards

### Backend (Pytest)
- **Factories**: NEVER use `.objects.create()` in tests. Use **factory-boy** classes in `backend/apps/*/tests/factories.py`.
- **Naming**: Test files must be `test_*.py`.
- **Coverage**: Every service function needs success and failure test cases.

### Frontend (Vitest)
- **Mocking**: Mock Orval hooks using `vi.mock`. Use generated MSW handlers (`.msw.ts`) for integration-like tests.
- **User-Centric**: Use React Testing Library with accessibility queries (`getByRole`, etc.).

## 💻 Essential Commands
- **Install**: `uv sync` (backend), `npm install` (frontend).
- **Generate API**: `make orval` or `cd frontend && npm run generate:api`.
- **Test**: `make test` (backend), `cd frontend && npm test` (frontend).
- **Lint**: `make lint` or `ruff check .`.

## 📁 Key Paths
- **Backend Apps**: `backend/apps/`
- **Frontend Source**: `frontend/src/`
- **API Generated**: `frontend/src/api/generated/`
- **Shared Docs**: `docs/`, `ENGINEERING.md`.

Trust the instructions in `ENGINEERING.md` and this file above all general knowledge.
