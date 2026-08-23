---
name: wedding-backend
description: "Backend patterns for Wedding Management System — Django Ninja Service Layer, multi-tenancy, authentication, exception handlers, model validations, atomic transactions, clean code. Load when implementing backend features, endpoints, or models."
---

# Wedding Backend Operational Playbook

Operational checklist for backend development (Django 5.2 + Django Ninja).

## Backend Development Checklist

- [ ] **Service Layer & CQRS Pattern**:
  - Delegate `GET` endpoints in `api.py` to `selectors/`.
  - Delegate mutation endpoints (`POST`, `PUT`, `PATCH`, `DELETE`) to `services/`.
  - Prohibit raw queries and business logic inside controllers (`api.py`).
  - See [Service Layer Pattern](../../../docs/architecture/concepts/service-layer-pattern.md) and [Query Selectors Pattern](../../../docs/architecture/concepts/query-selectors-pattern.md).
- [ ] **Query Selectors & Custom QuerySets**:
  - Keep pure read queries and aggregations in `selectors/` returning chainable lazy `CustomQuerySet` instances (subclasses of `TenantQuerySet` in `managers.py`).
  - Keep write rules and mutations exclusively in `services/`. FORBIDDEN pure read methods in `services/`.
  - See [Query Selectors Spec](../../../docs/reference/architecture-standards/query-selectors-spec.md) and [Create Query Selectors Guide](../../../docs/guides/backend/create-query-selectors.md).
- [ ] **Router operation_id**: Define an explicit `operation_id` on all `@router.<method>` endpoints for Orval client code generation.
- [ ] **Multi-Tenancy Enforcement**:
  - Query tenant models using `Model.objects.for_tenant(company)`. Never use unfiltered `.objects.all()` or `.objects.create()`.
  - Use `get_object_or_404_for_tenant(Model, company=company, uuid=uuid)` or `*_get_selector` for tenant-isolated lookups returning 404 on missing/unauthorized resources.
  - See [Multi-Tenancy Strategy](../../../docs/architecture/concepts/multi-tenancy-strategy.md).
- [ ] **Data Integrity & Model Validation**:
  - Inherit models from `BaseModel` (`apps/core/models.py`), which executes `full_clean()` automatically inside `save()`.
  - Only use `skip_clean=True` for bulk operations or migrations with explicit reasoning.
- [ ] **Static Typing**: Maintain strict static typing; `mypy` must pass without errors.
- [ ] **Atomic Transactions & N+1 Prevention**: Wrap multi-write services in `@transaction.atomic` or `with transaction.atomic():`. Pre-fetch relationships using `.select_related()` and `.prefetch_related()`.
- [ ] **Error Handling & Envelope**: Raise domain exceptions (`ApplicationError`, `BusinessRuleViolation`, `DomainIntegrityError`, `ObjectNotFoundError`). See [Error Envelope Spec](../../../docs/reference/api/error-envelope-spec.md).
- [ ] **Unit & Integration Testing**: Every public function in `services.py` and new API endpoint MUST be accompanied by unit tests in `apps/<app>/tests/test_services.py` (covering happy path + sad path) using factories. See [wedding-backend-testing](../wedding-backend-testing/SKILL.md) and [Backend Testing Spec](../../../docs/reference/testing/backend-testing-spec.md).
- [ ] **Clean Code & Comments**: Write code comments in PT-BR explaining "why" (never "what"). Follow [Commenting Standards](../../../docs/reference/architecture-standards/commenting-standards.md).