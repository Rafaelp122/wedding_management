---
name: wedding-backend
description: "Backend patterns for Wedding Management System — Django Ninja Service Layer, multi-tenancy, authentication, exception handlers, model validations, atomic transactions, clean code. Load when implementing backend features, endpoints, or models."
---

# Wedding Backend Operational Playbook

Operational checklist for backend development (Django 5.2 + Django Ninja).

## Backend Development Checklist

- [ ] **Service Layer Pattern**: Keep `api.py` strictly for routing, auth, request validation, and payload serialization. Delegate all business logic and database queries to `services.py`. See [Service Layer Pattern](../../../docs/4-explanation/architecture/service-layer-pattern.md).
- [ ] **Router operation_id**: Define an explicit `operation_id` on all `@router.<method>` endpoints for Orval client code generation.
- [ ] **Multi-Tenancy Enforcement**:
  - Query tenant models using `Model.objects.for_tenant(company)`. Never use unfiltered `.objects.all()` or `.objects.create()`.
  - Use `get_object_or_404_for_tenant(Model, company=company, uuid=uuid)` from `apps.core.shortcuts` for tenant-isolated lookups returning 404 on missing/unauthorized resources.
  - See [Multi-Tenancy Strategy](../../../docs/4-explanation/architecture/multi-tenancy-strategy.md).
- [ ] **Data Integrity & Model Validation**:
  - Inherit models from `BaseModel` (`apps/core/models.py`), which executes `full_clean()` automatically inside `save()`.
  - Only use `skip_clean=True` for bulk operations or migrations with explicit reasoning.
- [ ] **Static Typing**: Maintain strict static typing; `mypy` must pass without errors.
- [ ] **Atomic Transactions & N+1 Prevention**: Wrap multi-write services in `@transaction.atomic` or `with transaction.atomic():`. Pre-fetch relationships using `.select_related()` and `.prefetch_related()`.
- [ ] **Error Handling & Envelope**: Raise domain exceptions (`ApplicationError`, `BusinessRuleViolation`, `DomainIntegrityError`, `ObjectNotFoundError`). See [Error Envelope Spec](../../../docs/3-reference/api/error-envelope-spec.md).
- [ ] **Clean Code & Comments**: Write code comments in PT-BR explaining "why" (never "what"). Follow [Commenting Standards](../../../docs/3-reference/architecture-standards/commenting-standards.md).