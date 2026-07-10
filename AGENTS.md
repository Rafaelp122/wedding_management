# Wedding Management - Engineering Context (Shared)

## Tech Stack

- **Backend**: Python 3.12+, Django, Django Ninja (no DRF).
- **Frontend**: React, TypeScript, Vite, Tailwind CSS, shadcn/ui.
- **Tools**: Orval, Docker, Makefile, uv.
- **Infrastructure**: PostgreSQL (Neon), Cloud Run, R2 (ADR-004).

## Architecture (Strict)

### Backend

- **Service Layer**: Endpoints in `api.py` MUST only call `services.py`. Business logic never in the API layer.
- **Multi-tenancy**: Every service receives `company`, uses `Model.objects.for_tenant(company)` (ADR-009, ADR-016).
- **Data Integrity**: Models inherit `BaseModel` which runs `full_clean()` on `save()` (ADR-011).
- **operation_id** required on all routers (e.g. `weddings_list`).
- **Typing**: Strict static typing — `mypy` must pass.

### Frontend

- **Feature-based**: `src/features/<name>/` with `/components`, `/hooks`, `/pages`, `/types.ts`, `/utils`.
- **Design**: Read `docs/DESIGN.md` before UI work (colors, Dialog vs Sheet, micro-interactions).
- **shadcn/ui**: Base in `src/components/ui/`. Business components in feature folder. Compose + Tailwind over modifying ui/ files.
- **API**: FORBIDDEN to use `fetch`/`axios`. Use only Orval hooks from `src/api/generated/`.
- **Forms**: `react-hook-form` + `zod`. **Icons**: `lucide-react` only.

## Testing

### Backend (Pytest)
- FORBIDDEN `.objects.create()` — use factories in `backend/apps/*/tests/factories.py`.
- Service tests must be unit/isolated.
- Every `services.py` function needs success + failure tests.

### Frontend (Vitest & RTL)
- Import `render`/`screen`/`userEvent` from `@/test-utils` (never from `@testing-library/react` directly — it misses providers).
- Sonner is globally mocked in `test-setup.ts` — import `toast` directly, **no per-file `vi.mock("sonner")`**.
- Recharts: mock with `vi.mock("recharts", ...)` returning simple `<div>` elements with `data-testid`. See `FinancesDistributionChart.test.tsx` for the canonical pattern.
- Dialogs: every `DialogContent` **must** render `DialogTitle` + `DialogDescription`. Use `className="sr-only"` for loading/error/empty states.
- `isolate: false` — all `vi.mock` calls are shared. Centralize mocks in `test-setup.ts`, never per-file for shared deps.
- Prioritize `getByRole`/`getByLabelText`. Mock Orval hooks with `vi.mock`. Use `faker` for test data.

## Workflow

- **Commits**: Conventional Commits (e.g. `feat(weddings): add list endpoint`).
- **ADRs**: New file in `docs/ADR/` for structural changes.
- **Lint**: `make lint` or `ruff check .` before push. Pre-commit active.
- **Secrets**: Never commit. `detect-secrets` active.

## AI Rules

- **Read `docs/DESIGN.md`** before UI work.
- **Load skills on demand** (not proactively).
- **Docstrings and Comments**: Must follow the standard defined in [COMMENTING_STANDARDS.md](file:///home/rafael/.gemini/antigravity/worktrees/wedding_management/review-service-documentation-comments/docs/COMMENTING_STANDARDS.md). Write in Portuguese (PT-BR) for business explanations, use Google Style for docstrings, and never include references to AI/generation tools (like "Bolt", "Jules", "Copilot").

## Subagents

Dispatch subagents for 2+ file changes, multi-step logic, or complex searches.
Main conversation = only direct questions, single edits, coordination.

| Name | When to dispatch |
|---|---|
| **backend** | Django models, services, endpoints, migrations, tests, business logic |
| **frontend** | React components, pages, hooks, forms, Orval, API integration, tests |
| **design** | UI/UX design, layout, styling, theme, Tailwind, accessibility |
