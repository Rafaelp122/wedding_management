---
applyTo: "backend/apps/**/*.py"
---

# Backend Specific Instructions

- **Domain Driven**: Each app in `backend/apps/` should focus on its own domain.
- **Service Layer**: Business logic belongs in `services.py`. Functions should be pure when possible or explicitly handle side effects.
- **Security**: Services receive a `company` parameter. Always use `Model.objects.for_tenant(company)` for filtering QuerySets. Never trust client-provided IDs for ownership without verification.
- **Models**: Use the `BaseModel` and ensure `full_clean()` is called (handled automatically by `BaseModel.save()`).
- **Factories**: When writing tests, always import from the `factories.py` of the respective app.
- **API Response**: Use the `MUTATION_ERROR_RESPONSES` and `READ_ERROR_RESPONSES` from `apps.core.exceptions` for consistent API error handling.
