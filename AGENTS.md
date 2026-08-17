# Wedding Management - Global Engineering Context

## Tech Stack & Architecture Overview

- **Stack**: Python 3.12+ (Django Ninja) | React 19 + TypeScript + Vite + Tailwind CSS 4 + shadcn/ui.
- **Single Source of Truth (`docs/`)**: Documentation follows **Diátaxis** in `docs/`. Always consult `docs/README.md` before architectural or domain changes.
- **On-Demand Skills (`.agents/skills/`)**: Skills are task-specific operational playbooks loaded on demand (never proactively).

## Universal Guard-Rails (Non-Negotiable)

### Backend
- **Service Layer & CQRS**: Route handlers in `api.py` MUST delegate `GET` queries to `selectors/` and mutations (`POST`, `PUT`, `PATCH`, `DELETE`) to `services/`. No business logic or raw queries in controllers.
- **Query Selectors & Custom QuerySets**: Read queries and annotations reside in `selectors/` and `managers.py` (`TenantQuerySet`), returning chainable lazy querysets. FORBIDDEN pure read methods in `services/`.
- **Multi-Tenancy**: Every service/selector accepts `company` and queries via `Model.objects.for_tenant(company)` (ADR-009, ADR-016). Use `get_object_or_404_for_tenant` or `*_get_selector` for single lookups.
- **Data Integrity**: Models inherit `BaseModel` (`full_clean()` on `save()`). `mypy` strict static typing enforced.
- **Router Endpoints**: `operation_id` required on all router endpoints.

### Frontend
- **API Access**: FORBIDDEN to use `fetch` or `axios` directly. Use ONLY generated Orval hooks from `@/api/generated/`.
- **UI & Components**: Follow [DESIGN.md](DESIGN.md). Compose shadcn/ui primitives with Tailwind in `src/features/<name>/components/`. NEVER modify `src/components/ui/` files directly.
- **Forms & Icons**: `react-hook-form` + `zod`. `lucide-react` ONLY.

### Testing (`isolate: false`)
- **Backend**: FORBIDDEN `.objects.create()` — use factories in `apps/*/tests/factories.py`. `services.py` requires unit success/failure coverage. `selectors/` requires unit/isolated tenant coverage in `test_selectors.py`.
- **Frontend**: FORBIDDEN `vi.mock("@/api/generated/...")` or per-file data hook mocks. Centralize all mocks in `test-setup.ts` via `registerMockHook`. Import testing utilities from `@/test-utils`.

### Documentation & Comments
- **Diátaxis & Atomic Notes**: Follow **Diátaxis** and **Atomic Notes** in `docs/` ([documentation-standards](docs/3-reference/architecture-standards/documentation-standards.md)). Cross-link atomic notes without text duplication. Run `make check-docs`.
- **PT-BR & Code Comments**: Write comments/docstrings in Portuguese (PT-BR) following [commenting-standards](docs/3-reference/architecture-standards/commenting-standards.md). Use Google Style for public service methods.
- **No AI Mentions**: PROHIBITED to reference AI tools, assistants, or generators (e.g. "Bolt", "Jules", "Copilot") in comments or documentation.

## Subagents Dispatch Matrix

Dispatch subagents for multi-file changes, multi-step logic, or heavy investigations. Keep the main conversation thread for direct questions and coordination.

| Subagent | Role & Trigger |
| :--- | :--- |
| **`backend`** | Django models, services, endpoints, migrations, backend tests, business logic |
| **`frontend`** | React components, pages, custom hooks, forms, Orval integration, frontend tests |
| **`design`** | UI/UX layouts, Tailwind styling, theme tweaks, component accessibility |
