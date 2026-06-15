---
applyTo: "backend/apps/**/*.py"
---

# Backend Specific Instructions

- **Service Layer**: `api.py` endpoints call `services.py` only. Business logic never in the API layer.
- **Multi-tenancy**: Every service receives `company`. Use `Model.objects.for_tenant(company)` (ADR-009, ADR-016).
- **operation_id**: Required on all routers (e.g. `weddings_list`).
- **Typing**: Strict static typing — `mypy` must pass. Avoid `Any`.
- **Models**: Use `TenantModel` (inherits `BaseModel` — `full_clean()` runs on `save()`). Only `Company` inherits `BaseModel` directly.
- **Factories**: Tests use factories from `apps/*/tests/factories.py`. FORBIDDEN `.objects.create()` in tests.
- **API Error Responses**: Use `MUTATION_ERROR_RESPONSES` and `READ_ERROR_RESPONSES` from `apps.core.exceptions`.
