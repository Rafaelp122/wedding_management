# Wedding Management - Global Engineering Context

## Tech Stack & Architecture Overview

- **Stack**: Python 3.12+ (Django Ninja) | React 19 + TypeScript + Vite + Tailwind CSS 4 + shadcn/ui.
- **Single Source of Truth (`docs/`)**: Documentation follows **Diátaxis** in `docs/`. Always consult `docs/README.md` before architectural or domain changes.
- **On-Demand Skills (`.agents/skills/`)**: Skills are task-specific operational playbooks loaded on demand (never proactively).

## Universal Guard-Rails (Non-Negotiable)

### Backend
- **Service Layer**: Route handlers in `api.py` MUST ONLY delegate to `services.py`. No business logic or queries in controllers.
- **Multi-Tenancy**: Every service accepts `company` and queries via `Model.objects.for_tenant(company)` (ADR-009, ADR-016). Use `get_object_or_404_for_tenant` for single lookups.
- **Data Integrity**: Models inherit `BaseModel` (`full_clean()` on `save()`). `mypy` strict static typing enforced.
- **Router Endpoints**: `operation_id` required on all router endpoints.

### Frontend
- **API Access**: FORBIDDEN to use `fetch` or `axios` directly. Use ONLY generated Orval hooks from `@/api/generated/`.
- **UI & Components**: Follow [DESIGN.md](DESIGN.md). Compose shadcn/ui primitives with Tailwind in `src/features/<name>/components/`. NEVER modify `src/components/ui/` files directly.
- **Forms & Icons**: `react-hook-form` + `zod`. `lucide-react` ONLY.

### Testing (`isolate: false`)
- **Backend**: FORBIDDEN `.objects.create()` — use factories in `apps/*/tests/factories.py`. `services.py` requires unit success/failure coverage.
- **Frontend**: FORBIDDEN `vi.mock("@/api/generated/...")` or per-file data hook mocks. Centralize all mocks in `test-setup.ts` via `registerMockHook`. Import testing utilities from `@/test-utils`.

### Documentation & Comments
- **PT-BR & Standards**: Write comments/docstrings in Portuguese (PT-BR) following [commenting-standards](docs/3-reference/architecture-standards/commenting-standards.md). Use Google Style for public service methods.
- **No AI Mentions**: PROHIBITED to reference AI tools, assistants, or generators (e.g. "Bolt", "Jules", "Copilot") in comments.

## Subagents Dispatch Matrix

Dispatch subagents for multi-file changes, multi-step logic, or heavy investigations. Keep the main conversation thread for direct questions and coordination.

| Subagent | Role & Trigger |
| :--- | :--- |
| **`backend`** | Django models, services, endpoints, migrations, backend tests, business logic |
| **`frontend`** | React components, pages, custom hooks, forms, Orval integration, frontend tests |
| **`design`** | UI/UX layouts, Tailwind styling, theme tweaks, component accessibility |
