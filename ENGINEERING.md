# Wedding Management - Engineering Context (Shared)

This file serves as the Single Source of Truth for all AI agents and developers working on this project.

## Tech Stack

- **Backend**: Python 3.12+, Django, Django Ninja (Strict: No DRF).
- **Frontend**: React, TypeScript, Vite, Tailwind CSS, Shadcn UI.
- **Tools**: Orval (Contract-driven API), Docker, Makefile, uv (Python pkg manager).

## Architectural Rules (Strict)

### Backend (apps/)

- **Service Layer Pattern**: Endpoints in `api.py` must only call functions in `services.py`.
- **Multi-tenancy**: Every service must explicitly receive `user=request.user` for filtering.
- **Operations**: Always define `operation_id` in routers (e.g., `weddings_list`).
- **Data Integrity**: Models inherit from `BaseModel` which executes `full_clean()` on `save()`.
- **Deletion**: Hard delete is the default. Do not implement soft delete.
- **Error Handling**: Use `MUTATION_ERROR_RESPONSES` and `READ_ERROR_RESPONSES` from core.

### Frontend (src/)

- **Feature-Based Architecture**: Organized by features in `src/features/<feature_name>/`.
  - Structure: `/components`, `/hooks`, `/pages`, `/types.ts`, `/utils`.
- **API Consumption**: FORBIDDEN to use `fetch` or `axios` manually. Use exclusively Orval-generated hooks in `src/api/generated/`.
- **Typing**: Strict TypeScript in all components and hooks.

## Workflow Conventions

- **Commits**: Follow Conventional Commits (e.g., `feat(weddings): add list endpoint`).
- **State Management**: Global state via Zustand in `src/stores/`.
- **Style**: Follow Ruff (Python) and ESLint (TS) standards.
