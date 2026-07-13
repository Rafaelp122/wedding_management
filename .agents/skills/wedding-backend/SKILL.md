---
name: wedding-backend
description: "Backend patterns for Wedding Management System — Django Ninja Service Layer, multi-tenancy, authentication, exception handlers, model validations, atomic transactions, clean code. Load when implementing backend features, endpoints, or models."
---

# Wedding Management Backend

Django 5.2 + Django Ninja Extra — patterns, security, and clean code for the Wedding Management System backend.

---

## 1. Architectural Rules (Mandatory)

### Service Layer Pattern
- Endpoints in `api.py` **MUST ONLY** contain HTTP routing, authentication, request validation, and payload serialization.
- All business logic, database queries, and data manipulation **MUST** reside inside functions within `services.py`.
- Flow: `api.py` (Controller) → `services.py` (Business Logic) → `models.py` (Data Layer).

### Multi-tenancy Enforcement
- Every service function that interacts with tenant-owned models must receive a `company` object parameter.
- Always query models using `Model.objects.for_tenant(company)`. Never use `.objects.all()` or `.objects.filter()` without tenant isolation.
- For nested resources, verify both the resource and its parent belong to the same tenant company.

### Data Integrity & Model Validations
- Models must inherit from `BaseModel` (`apps/core/models.py`).
- `BaseModel` calls `full_clean()` in `save()`. Inputs must be valid per field constraints.
- Pass `skip_clean=True` only for bulk operations, migrations, or fixtures (ADR-011).

### Typing
- Strict static typing enforced. `mypy` must pass without errors.

---

## 2. API Design with Django Ninja

### Route Definitions
```python
from ninja import Router, Schema
from uuid import UUID

# Always define operation_id for correct Orval generation
router = Router()

class GuestCreateIn(Schema):
    first_name: str
    last_name: str
    email: str
    rsvp_status: str

class GuestOut(Schema):
    id: UUID
    first_name: str
    last_name: str
    email: str
    rsvp_status: str

@router.post("/guests", response={201: GuestOut}, operation_id="guests_create")
def create_guest(request: HttpRequest, payload: GuestCreateIn):
    user = require_user(request.user)
    guest = services.create_guest(
        company=user.company,
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        rsvp_status=payload.rsvp_status,
    )
    return 201, guest
```

### Service Layer
```python
from apps.companies.models import Company
from .models import Guest

def create_guest(*, company: Company, first_name: str, last_name: str, email: str, rsvp_status: str) -> Guest:
    email_exists = Guest.objects.for_tenant(company).filter(email=email).exists()
    if email_exists:
        raise ValueError("A guest with this email is already registered for this wedding.")

    guest = Guest(
        company=company,
        first_name=first_name,
        last_name=last_name,
        email=email,
        rsvp_status=rsvp_status,
    )
    guest.save()  # full_clean() runs automatically
    return guest
```

---

## 3. Authentication & Authorization

- **API-level auth**: `JWTAuth()` is configured globally in `config/api.py` — all endpoints require JWT Bearer token by default.
- **Endpoint guard**: Use `require_user(request.user)` from `apps.users.auth` as an explicit guard clause that narrows `AuthContextUser` to `User` and raises `AuthenticationRequiredError` (401) if unauthenticated.
- **`user.company`**: Access the tenant company via `user.company`, never `request.user.company` directly.

```python
from ninja import Router
from apps.users.auth import require_user
from apps.users.types import AuthRequest

router = Router()

@router.get("/items", response=list[ItemOut], operation_id="items_list")
def list_items(request: AuthRequest):
    user = require_user(request.user)
    return ItemService.list(company=user.company)
```

---

## 4. Safe Exception Handlers

Do not expose database errors or raw stack traces in production. Define custom exception handlers:

```python
from ninja import NinjaAPI
from django.core.exceptions import ObjectDoesNotExist, ValidationError

api = NinjaAPI()

@api.exception_handler(ObjectDoesNotExist)
def handle_not_found(request, exc):
    return api.create_response(
        request,
        {"status": "error", "error": {"code": "NOT_FOUND", "message": "The requested resource could not be found."}},
        status=404,
    )

@api.exception_handler(ValidationError)
def handle_validation_error(request, exc):
    return api.create_response(
        request,
        {"status": "error", "error": {"code": "VALIDATION_FAILED", "message": str(exc)}},
        status=400,
    )
```

---

## 5. Database & Transactions

- Use `transaction.atomic` for services performing multiple write operations.
- Use `.select_related()` for FK relations and `.prefetch_related()` for M2M/reverse relations to avoid N+1 queries.
- QuerySet method chaining (`.filter().select_related()`) is idiomatic — not a Law of Demeter violation.

---

## 6. Secrets & Data Privacy

- Never commit API keys, webhook secrets, or database URLs. Use environment variables and keep `detect-secrets` pre-commit hooks active.
- PII (guest emails, phone numbers): store and process securely. Only return fields that are absolutely necessary in API payloads.

---

## 7. Clean Code — Python/Django

### Naming
- `snake_case` for variables, functions, modules. `PascalCase` for classes.
- Suffixes: `Service` (e.g. `WeddingService`), `Manager` (e.g. `TenantManager`) encouraged.
- Method names: verbs for actions (`get_supplier`, `create_wedding`), nouns for DTOs/Schemas.
- Avoid generic names like `d` or `data`. Use `elapsed_time_in_days` or `supplier_list`.

### Functions (SRP)
- Route handlers only validate input and delegate to `services.py`.
- Prefer keyword-only arguments: `def create_supplier(*, company, data)`.
- Pure functions — no secret mutations of global state or passed arguments.

### DTOs
- Use Pydantic Schemas or `dataclasses` for API payloads. No business logic inside DTOs.
- API schemas auto-generate OpenAPI docs and Orval hooks.

### Error Handling & Null Safety
- Raise domain exceptions (`ApplicationError` subclasses) — never return error codes/dicts.
- Returning `None` is acceptable — always type it explicitly (`User | None`). Let `mypy` enforce null-checks.

### Comments & Docstrings
- Prefer self-explanatory code over redundant comments (e.g. never write `# save the user` followed by `user.save()`).
- Comments and docstrings must follow the guidelines in [COMMENTING_STANDARDS.md](../../../docs/COMMENTING_STANDARDS.md).
- Use **Português (PT-BR)** for business rules, model validations, and logic explanations. Keep technical terms in English.
- Code comments must focus on the "why" (business rules, workarounds, performance optimizations), never on the "what".
- Enforce **Google Style** docstrings for complex or public methods, detailing `Args`, `Returns`, and `Raises`.
- **CRITICAL**: Never reference AI coding assistants, code generation tools, or development environments in code comments (such as "Bolt", "Jules", "Copilot"). Focus comments strictly on technical explanation.

---

## 8. Exception Handling

### Project Exception Hierarchy (`apps/core/exceptions.py`)

- `ApplicationError` (400) — base exception with `status_code`, `detail`, and `code`.
- `AuthenticationRequiredError` (401) — authentication required. Raised by `require_user()`.
- `ObjectNotFoundError` (404) — resource not found. Replaces `get_object_or_404` in the Service Layer.
- `BusinessRuleViolation` (422) — business rule prevents processing (e.g. ADR-010 Zero Tolerance).
- `DomainIntegrityError` (409) — cross-wedding validation, data integrity conflicts.

### Standard "Get by UUID" Pattern

Use the project's helper `get_object_or_404_for_tenant` from `apps.core.shortcuts`:

```python
from apps.core.shortcuts import get_object_or_404_for_tenant

wedding = get_object_or_404_for_tenant(
    Wedding,
    company=company,
    uuid=uuid,
    select_related=["venue"],      # optional FK optimization
    prefetch_related=["guests"],   # optional M2M optimization
)
```

This function:
- Filters by tenant via `Model.objects.for_tenant(company)` ✅
- Returns a user-safe 404 (`ObjectNotFoundError`) if not found ✅
- Accepts `select_related` / `prefetch_related` for N+1 prevention ✅
- Supports custom `detail` and `code` for error messages ✅
- Handles malformed UUIDs gracefully (ValueError → 404) ✅

> **Do NOT use Django's `get_object_or_404`** — it doesn't filter by tenant and leaks existence info.
> **Do NOT use `.filter(uuid=uuid).first()` + manual raise** — the helper already does this and is the project convention (used 40+ times across services).

### Fail-Fast in Services

Raise domain exceptions immediately with descriptive `detail` and machine-readable `code`:

```python
if contract.actual_amount != expense.actual_amount:
    raise BusinessRuleViolation(
        detail="Expense amount must match contract amount.",
        code="amount_mismatch_contract",
    )
```

### Exception Chaining

Use `raise ... from e` to preserve the full error trail:

```python
from django.db import IntegrityError
from apps.core.exceptions import DomainIntegrityError

try:
    with transaction.atomic():
        wedding = get_object_or_404_for_tenant(Wedding, company=company, uuid=uuid)
        wedding.status = "CANCELED"
        wedding.save()
except IntegrityError as e:
    raise DomainIntegrityError(
        detail="Cannot cancel wedding due to existing contracts.",
        code="wedding_cancel_conflict",
    ) from e
```

### Security

- Never expose database errors, SQL, stack traces, or internal paths in API responses.
- Exception handlers in the Ninja API config should obfuscate internal details.
- `detail` messages must be user-safe — no implementation details.

---

## 9. Validation Layers

Validation occurs at three levels, in priority order:

### 1. Schema (Pydantic) — Earliest Boundary, Fail-Fast

Cross-field constraints and field ranges at the API boundary. Returns structured 422 errors.

```python
class EventIn(Schema):
    start_time: datetime
    end_time: datetime | None = None
    reminder_minutes_before: int = 60

    @model_validator(mode="after")
    def validate_event(self) -> "EventIn":
        if self.start_time and self.end_time and self.end_time < self.start_time:
            raise ValueError("End time must not be before start time.")
        if self.reminder_minutes_before < 0:
            raise ValueError("Reminder minutes must be positive.")
        return self
```

### 2. Model (Django) — Automatic via `BaseModel.full_clean()`

Field-level constraints enforced on `save()`:
- `max_length`, `null`, `blank`, `unique`
- No manual intervention needed — inherited from `BaseModel`

### 3. Service — Business Rules & Cross-Model Checks

Complex rules that span multiple models or require database lookups:
- BR-F01 Zero Tolerance, BR-F02 Legal Anchor
- Cross-wedding integrity checks (`category.wedding != expense.wedding`)
- Multi-tenancy isolation
- Use `raise BusinessRuleViolation` for business rule failures
- Use `raise DomainIntegrityError` for cross-entity conflicts

---

## 10. Common Pitfalls (Avoid These!)

### ❌ Forgetting `operation_id` on Router Endpoints
Orval hooks won't be generated. Every `@router.get/post/...` must have `operation_id`.

### ❌ Using Django's `get_object_or_404` in Services
Leaks existence information to unauthorized tenants and doesn't filter by company. Use `get_object_or_404_for_tenant` from `apps.core.shortcuts` instead — it's type-safe, tenant-aware, and already used 40+ times across the project.

### ❌ Accessing `request.user.company` Directly
Can fail if user is `AuthContextUser` instead of `User`. Always use `user = require_user(request.user)` first.

### ❌ Not Using `transaction.atomic` for Multi-Write Services
If a service creates + updates multiple models, wrap in `with transaction.atomic():`. Otherwise a partial failure leaves inconsistent data.

### ❌ Forgetting `.select_related()` / `.prefetch_related()`
Results in N+1 queries. Always prefetch FK/M2M relations in list/detail endpoints.

### ❌ Returning Python `float` for Monetary Values
Causes floating-point rounding errors. Always use `Decimal` for monetary amounts in schemas and models.

### ❌ Using `.objects.create()` or `.objects.bulk_create()` Without `for_tenant`
Bypasses tenant isolation. Always go through `Model.objects.for_tenant(company)` first.

### ❌ Hardcoding File Paths or URLs
Breaks in Docker/Cloud Run. Use Django settings or environment variables.

### ❌ Raising Generic `Exception` or `RuntimeError`
Consumers can't distinguish error types. Always raise a domain exception from `apps/core/exceptions.py`.

### ❌ Passing `skip_clean=True` Without Good Reason
Bypasses model validation. Only use for bulk operations, migrations, or fixtures. Document why in a comment.