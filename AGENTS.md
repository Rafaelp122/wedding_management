# Wedding Management - Engineering Context (Shared)

## 🚀 Tech Stack

- **Backend**: Python 3.12+, Django, Django Ninja (Strict: No DRF).
- **Frontend**: React, TypeScript, Vite, Tailwind CSS, shadcn/ui.
- **Tools**: Orval (Contract-driven API), Docker, Makefile, uv (Python pkg manager).
- **Infrastructure**: PostgreSQL (Neon), Cloud Run, R2 (Storage via ADR-004).

## 🏗 Architectural Rules (Strict)

### Backend (apps/)

- **Service Layer Pattern**: Endpoints in `api.py` MUST ONLY call functions in `services.py`. Business logic never goes in the API layer.
- **Multi-tenancy**: Every service must explicitly receive `company` and use `Model.objects.for_tenant(company)` for mandatory filtering (see ADR-009 and ADR-016).
- **Data Integrity**: Models inherit from `BaseModel` which runs `full_clean()` on `save()` (see ADR-011).
- **Operations**: Always define `operation_id` on routers (e.g. `weddings_list`) for correct Orval generation.
- **Typing**: The project uses strict static typing. `mypy` must pass without errors.

### Frontend (src/)

- **Feature-Based Architecture**: Organize by features in `src/features/<feature_name>/`.
  - Structure: `/components`, `/hooks`, `/pages`, `/types.ts`, `/utils`.
- **shadcn/ui**:
  - Base UI components live in `src/components/ui/`.
  - Business components live in the feature folder.
  - Prefer composition and Tailwind over modifying files in the `ui` folder directly.
- **API Consumption**: FORBIDDEN to use `fetch` or `axios` manually. Use only Orval-generated hooks in `src/api/generated/`.
- **Forms**: Use `react-hook-form` integrated with `zod` for validation.
- **Icons**: Use only `lucide-react`.

## 🧪 Testing Standards (Mandatory)

### 🐍 Backend (Pytest)

- **Factories Over DB**: FORBIDDEN to use `.objects.create()` in tests. Use factory classes in `backend/apps/*/tests/factories.py`.
- **Isolation**: Service tests must be unit/isolated. Use Factories for supporting data.
- **Coverage**: Every function in `services.py` must have at least one success and one failure test (expected exception).

### ⚛️ Frontend (Vitest & RTL)

- **User-Centric**: Test user behavior. Prioritize accessibility queries (`getByRole`, `getByLabelText`).
- **Mocking**: Mock Orval hooks using `vi.mock`. Never make real API calls in tests.
- **Data**: Use `faker` to generate test payloads and consistent API mocks.

## 🔄 Workflow Conventions

- **Commits**: Follow Conventional Commits pattern (e.g. `feat(weddings): add list endpoint`).
- **ADRs**: Structural changes MUST generate a new file in `docs/ADR/` following sequential numbering.
- **Lint/Format**: Run `make lint` or `ruff check .` before any push. Pre-commit must be active.
- **Secrets**: Never commit secrets. We use `detect-secrets` to prevent leaks.

## 🤖 AI Agent Guidelines

- **Use subagents** for specialized tasks (backend, frontend, testing, design, review)
- **Load skills on demand** when you need deep domain knowledge:

| Domain | Skill |
|---------|-------|
| Backend Django Ninja, Service Layer, security, auth | `wedding-backend` |
| Frontend architecture, Orval, forms, icons | `wedding-frontend` |
| Backend testing — pytest, factories, mocking | `wedding-backend-testing` |
| Frontend testing — Vitest, MSW, Playwright E2E | `wedding-frontend-testing` |
| Business rules (finances, logistics, scheduler) | `wedding-business-rules` |
| shadcn/ui components and composition | `shadcn` |
| Tailwind CSS v4 + shadcn/ui setup, dark mode | `tailwind-v4-shadcn` |
| React Hook Form performance, useWatch, useFieldArray | `react-hook-form` |
| Docker expert, best practices, security | `docker-expert` |
| Google Cloud Run deployment | `cloud-run-basics` |
| Vercel deployment | `deploy-to-vercel` |
| Interface design | `frontend-design` |
