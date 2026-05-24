---
name: wedding-backend-testing
description: "Backend testing standards for Wedding Management System — pytest, factories, fixtures, mocking, multitenancy tests, Django patterns, coverage. Load when writing or reviewing backend tests."
---

# Wedding Backend Testing Standards

Testing standards for the Wedding Management System backend — pytest + Django.

---

## 1. Tooling

`pytest`, `pytest-django`, `factory-boy`, `faker` (pt_BR), `pytest-cov`, `pytest-mock`, `django-zeal` (N+1 detection).

---

## 2. Directory Structure

### 2.1 Single Entity (e.g. `weddings`)

```
apps/my_app/tests/
├── conftest.py          # Domain-specific fixtures
├── factories.py         # Model blueprints
├── test_models.py       # Model integrity and metadata
├── test_services.py     # Pure business logic
└── test_apis.py         # HTTP contract, security, isolation
```

### 2.2 Multiple Entities (e.g. `logistics`, `finances`)

```
apps/my_app/tests/
├── conftest.py
├── factories.py
├── entity_a/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_services.py
│   └── test_apis.py
└── entity_b/
    ├── __init__.py
    └── ...
```

`__init__.py` is required in each entity subdirectory to avoid module name collisions.

### 2.3 Global vs Local Conftest

- `backend/conftest.py` (Global): shared fixtures (`user`, `auth_client`, global factory registration)
- `apps/<app>/tests/conftest.py` (Local): domain-specific fixtures

---

## 3. Test Layers

### 3.1 Models (`test_models.py`)

Tests database integrity and metadata:
- Field validations (`max_length`, `null`, `blank`)
- Rules via `full_clean` (internal state)
- `__str__`, `Meta.ordering`
- Purely local state transitions (no external orchestration)

### 3.2 Services (`test_services.py`)

Complex business logic. The Service Layer receives already-validated instances.

- Pure business rules (calculations, state validations)
- **Fail Fast**: Service raises exceptions (`BusinessRuleViolation`, `DomainIntegrityError`) with inconsistent data
- **Isolation**: Scope filtering in `list` and `create`

**Coverage rule**: Every public function in `services.py` must have **≥1 success + ≥1 failure** test.

### 3.3 APIs (`test_apis.py`)

Validates HTTP contract and security:

- **Happy paths**: 200/201 with correct JSON
- **Isolation (Multitenancy)**: Accessing another planner's UUID → `404 Not Found` (NEVER `403 Forbidden`)
- **Security**: No token → `401 Unauthorized`
- **Integrity**: Malformed UUID → `422 Unprocessable Entity`

---

## 4. Factories

`FORBIDDEN .objects.create()` in tests. Use factories from `backend/apps/*/tests/factories.py`.

```python
# ✅ CORRECT
from apps.weddings.tests.factories import WeddingFactory
wedding = WeddingFactory(company=user.company, bride_name="Maria")

# ❌ WRONG
wedding = Wedding.objects.create(company=user.company, bride_name="Maria", date="2026-01-01")
```

### Factory Independence

Factories in one app must not depend on factories from another app. Avoid cross-app `SubFactory`.

```python
# ❌ AVOID — cross-app SubFactory
class ExpenseFactory(factory.django.DjangoModelFactory):
    contract = factory.SubFactory("apps.logistics.tests.factories.ContractFactory")

# ✅ PREFER — create minimal dependencies in the test
def test_expense_creation(user):
    category = BudgetCategoryFactory(company=user.company)
    expense = ExpenseFactory(company=user.company, category=category, contract=None)
```

---

## 5. Fixtures (pytest)

### Scopes

| Scope | When to use |
|-------|------------|
| `function` (default) | Each test gets a fresh instance |
| `class` | Share across tests in the same class |
| `module` | Database connection per module |
| `session` | Global configuration (logging, engine) |

```python
@pytest.fixture(scope="session")
def database_connection():
    db = Database()
    db.connect()
    yield db
    db.disconnect()

@pytest.fixture(scope="module")
def api_client():
    client = APIClient()
    client.authenticate()
    yield client
    client.logout()

@pytest.fixture  # function scope (default)
def temp_file():
    f = tempfile.NamedTemporaryFile(mode='w', delete=False)
    yield f.name
    os.unlink(f.name)
```

### Fixture Factories

```python
@pytest.fixture
def make_user():
    users = []
    def _make_user(name, email=None):
        user = User(name=name, email=email or f"{name}@example.com")
        users.append(user)
        return user
    yield _make_user
    for user in users:
        user.delete()

def test_multiple_users(make_user):
    user1 = make_user("Alice")
    user2 = make_user("Bob", email="bob@test.com")
    assert user1.name == "Alice"
    assert user2.email == "bob@test.com"
```

### Autouse

```python
@pytest.fixture(autouse=True)
def reset_database():
    clear_database()
    seed_test_data()
```

---

## 6. Parametrization

```python
@pytest.mark.parametrize("input_value,expected", [
    ("valid@email.com", True),
    ("invalid-email", False),
])
def test_email_validation(input_value, expected):
    assert is_valid_email(input_value) == expected

@pytest.mark.parametrize("x", [0, 1])
@pytest.mark.parametrize("y", [2, 3])
def test_combinations(x, y):
    # Runs 4 times: (0,2), (0,3), (1,2), (1,3)
    assert x < y
```

---

## 7. Mocking

```python
from unittest.mock import patch

def test_create_wedding_triggers_budget_creation(user, wedding_payload):
    with patch("apps.finances.services.BudgetService.create") as mock_budget:
        WeddingService.create(company=user.company, data=wedding_payload)
    mock_budget.assert_called_once()

def test_create_draft_does_not_trigger_budget(user, draft_payload):
    with patch("apps.finances.services.BudgetService.create") as mock_budget:
        WeddingService.create_draft(company=user.company, data=draft_payload)
    mock_budget.assert_not_called()

def test_get_user_env(monkeypatch):
    monkeypatch.setenv("USER", "testuser")
    assert os.getenv("USER") == "testuser"
```

---

## 8. Markers

```python
@pytest.mark.slow
def test_massive_data_export(): ...

@pytest.mark.integration
def test_api_workflow(): ...

@pytest.mark.skip(reason="Feature not implemented")
def test_future(): ...

@pytest.mark.xfail(reason="Known bug")
def test_buggy(): ...
```

Run: `pytest -m "not slow"` for fast cycles, `pytest -m integration` for integration.

---

## 9. Naming Convention

- **Classes**: `Test<ServiceOrModelName>`
- **Methods**: `test_<behavior>_<scenario>_<expected_outcome>`
  - `test_create_installment_with_invalid_value_raises_error`
  - `test_pay_paid_installment_raises_business_rule_violation`

---

## 10. Test Code Quality Rules

### No Empty Stubs

```python
# ❌ FORBIDDEN
def test_something(self):
    pass

# ✅ CORRECT — use skip with reason
@pytest.mark.skip(reason="TODO: implement after BR-F02")
def test_something(self): ...
```

### No Debug Files in tests/

Files like `test_jwt_debug.py` with `print()` or `breakpoint()` do not belong in the test directory.

### No Test Duplication

Two files testing the same scenarios must be consolidated. One file per layer per entity.

### Pre-Refactor Coverage (Golden Rule)

1. Write tests that pass against current code (baseline)
2. Refactor or add functionality
3. Verify old tests still pass + add new tests

Never blindly refactor a service with 0% coverage.

---

## 11. What NOT to Test

- Django ORM (`.save()` persists, basic filters)
- External libraries (Pydantic, Django Ninja)
- Pure framework logic (Schema validates basic types without business rules)
- Exhaustive 422 for every field with wrong types — trust Pydantic

**Focus on YOUR rules and YOUR contracts.**

---

## 12. Static Security Audit

Located at `apps/core/tests/test_security_audit.py`, uses AST to ensure no UUID instance endpoint is created without an explicit authorization call. CI breaks if violated.

---

## 13. Cheat Sheet — Universal Scenarios

### Business Rules (Highest Priority)
- Happy paths: operation with valid data returns expected result
- Side effects: tested via mocks
- Sad paths: invalid data raises the correct exception
- Domain invariants: invalid state can never be reached

### Isolation & Security (Multitenancy)
- User A cannot read, modify, or delete User B's data
- Errors never leak resource existence (`404`, never `403`)

### API Contract
- Correct payload → status (200/201) and expected JSON
- Trust Pydantic/Ninja for type validation

### Boundaries & Edge Cases
For numeric or size fields: `value = 0`, `value = -1`, `value = max`, `value = max + 1`, `value = None`

### Concurrency & Performance
- Do not simulate race conditions in Pytest (flaky tests)
- Test mechanism existence: was `select_for_update` called? Does the `UniqueConstraint` exist?
- N+1: Trust `django-zeal` + `--nplusone-raise` in CI

### Regression
- Every fixed bug gets a test reproducing that bug
- The test must fail on the bug commit and pass on the fix commit

---

## 14. References

For deep domain knowledge:
- Load `wedding-backend` for Service Layer, Schemas, auth, transactions
- Load `wedding-business-rules` for business rules (BR-F01 through BR-F11, etc.)
