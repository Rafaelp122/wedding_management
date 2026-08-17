---
name: wedding-backend-testing
description: "Backend testing standards for Wedding Management System — pytest, factories, fixtures, mocking, multitenancy tests, Django patterns, coverage. Load when writing or reviewing backend tests."
---

# Wedding Backend Testing Playbook

Operational checklist for backend test suites (`pytest` + Django).

## Backend Testing Checklist

- [ ] **Forbidden `.objects.create()`**: ALWAYS use Model Factories located in `apps/*/tests/factories.py` (e.g. `WeddingFactory(company=user.company)`). Direct `.objects.create()` is strictly forbidden.
- [ ] **Service Unit Isolation**: Test `services.py` functions in isolation. Pass explicit `company` objects and isolate external dependencies cleanly.
- [ ] **Coverage Rule for Services**: Every public function in `services.py` MUST have at least **1 success (happy path)** test and at least **1 failure (sad path / exception)** test.
- [ ] **Coverage Rule for Selectors**: Every selector in `selectors/` MUST have unit/isolation tests in `test_selectors.py` verifying:
  - Multi-tenant isolation (`for_tenant`).
  - Correct query filters, annotations and chainable methods (`CustomQuerySet`).
  - Exception handling (`ObjectNotFoundError` on missing lookups).
- [ ] **Directory & File Layout**: Follow standard placement (`apps/<app>/tests/test_models.py`, `test_services.py`, `test_selectors.py`, `test_apis.py`). Include `__init__.py` in nested entity test subdirectories.
- [ ] **Multi-Tenancy Test Isolation**: Verify that API endpoints return `404 Not Found` (never 403 or raw exceptions) when attempting to access another tenant company's resources.
- [ ] **Test Naming Convention**: Class `Test<Name>`, method `test_<behavior>_<scenario>_<expected_outcome>`.
- [ ] **Strict Typing in Tests (`mypy`)**: All test functions and methods must declare explicit return types (`-> None`) and typed fixture parameters (`disallow_untyped_defs = true`, `check_untyped_defs = true`).
- [ ] **No Empty Stubs or Debug Files**: Do not leave `pass` stubs or debug files with `breakpoint()`/`print()` in test packages; use `@pytest.mark.skip(reason=...)` when skipping tests.
- [ ] **Execution & Standards Reference**:
  - Running pytest suite & test markers: [Run Pytest Suite Guide](../../../docs/2-how-to/backend/run-pytest-suite.md)
  - Full architectural testing standards & cheat sheet: [Backend Testing Spec](../../../docs/3-reference/testing/backend-testing-spec.md) | [Testing Index](../../../docs/3-reference/testing/index.md)
