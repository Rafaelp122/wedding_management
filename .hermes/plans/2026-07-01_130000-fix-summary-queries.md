# PR 2 — Consolidar queries duplicadas nos summary services

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Consolidar 2 queries separadas em 1 `aggregate()` em três summary services do dashboard.

**Architecture:** Manter assinatura e tipo de retorno (tuples) inalterados. Mudar apenas a implementação interna de cada método.

**Tech Stack:** Django ORM, PostgreSQL, pytest

---

## Contexto

### Problemas identificados

| # | Método | Queries atuais | Fix |
|---|---|---|---|
| 1 | `FinancialSummaryService.overdue_installments()` | `aggregate(total=Sum(...))` + `.count()` | 1 `aggregate(total=Sum, count=Count)` |
| 2 | `TaskSummaryService.wedding_task_stats()` | `.count()` + `.filter(is_completed=True).count()` | 1 `aggregate(total=Count, completed=Count+filter)` |
| 3 | `ContractSummaryService.wedding_contract_stats()` | `.exclude(status=CANCELED).count()` + `.filter(status=SIGNED).count()` | 1 `aggregate(total=Count+~Q, signed=Count+Q)` |

### Padrão

O padrão `COUNT(DISTINCT ...) FILTER (WHERE ...)` já é usado no projeto:
```python
# dashboard_service.py:62-85
.annotate(
    incomplete_tasks=Count("task_records", filter=Q(...), distinct=True),
    pending_installments=Count("installment_records", filter=Q(...), distinct=True),
)
```

### Retorno

Todos os três métodos retornam tuples:
- `overdue_installments()` → `tuple[Decimal, int]` (amount, count)
- `wedding_task_stats()` → `tuple[int, int]` (completed, total)
- `wedding_contract_stats()` → `tuple[int, int]` (signed, total)

Nenhum caller deprecado — todos são chamados apenas de `dashboard_service.py`.

---

## Arquivos que vão mudar

| Arquivo | Mudança |
|---|---|
| `backend/apps/weddings/services/summaries/financial.py:35-43` | `overdue_installments()` → 1 aggregate |
| `backend/apps/weddings/services/summaries/task.py:26-31` | `wedding_task_stats()` → 1 aggregate |
| `backend/apps/weddings/services/summaries/contract.py:21-28` | `wedding_contract_stats()` → 1 aggregate |

Nenhum teste precisa mudar — a assinatura e retorno são idênticos.

---

## Task 1: Fix `overdue_installments()` — 2 queries → 1

**Objective:** Consolidar `aggregate(total=Sum(...))` + `.count()` em um único `aggregate()`.

**Files:**
- Modify: `backend/apps/weddings/services/summaries/financial.py:35-43`
- Test: `backend/apps/weddings/tests/test_services.py::TestFinancialSummaryService::test_overdue_installments_*` (existentes)

**Step 1: Modificar `overdue_installments()`**

```python
# ANTES (financial.py:35-43)
@staticmethod
def overdue_installments(
    *, company: Company, today: date | None = None
) -> tuple[Decimal, int]:
    """Return total amount and count of overdue installments."""
    today = today or date.today()
    qs = Installment.objects.for_tenant(company).filter(
        Q(status=Installment.StatusChoices.OVERDUE)
        | Q(status=Installment.StatusChoices.PENDING, due_date__lt=today)
    )
    amount = qs.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    return amount, qs.count()

# DEPOIS
@staticmethod
def overdue_installments(
    *, company: Company, today: date | None = None
) -> tuple[Decimal, int]:
    """Return total amount and count of overdue installments."""
    from django.db.models import Count

    today = today or date.today()
    result = Installment.objects.for_tenant(company).filter(
        Q(status=Installment.StatusChoices.OVERDUE)
        | Q(status=Installment.StatusChoices.PENDING, due_date__lt=today)
    ).aggregate(
        total=Sum("amount"),
        count=Count("id"),
    )
    return (
        result["total"] or Decimal("0.00"),
        result["count"],
    )
```

Adicionar import no topo (já existe `Sum`, adicionar `Count`):
```python
from django.db.models import Count, Q, Sum
```

**Step 2: Verificar que testes passam**

Run: `cd backend && python -m pytest apps/weddings/tests/test_services.py::TestFinancialSummaryService::test_overdue_installments_returns_amount_and_count apps/weddings/tests/test_services.py::TestFinancialSummaryService::test_overdue_installments_empty -v`
Expected: Ambos passam

**Step 3: Commit**

```bash
git add backend/apps/weddings/services/summaries/financial.py
git commit -m "fix(summaries): consolidate overdue_installments into single aggregate"
```

---

## Task 2: Fix `wedding_task_stats()` — 2 queries → 1

**Objective:** Consolidar `tasks.count()` + `tasks.filter(is_completed=True).count()` em um único `aggregate()`.

**Files:**
- Modify: `backend/apps/weddings/services/summaries/task.py:26-31`
- Test: `backend/apps/weddings/tests/test_services.py::TestTaskSummaryService::test_wedding_task_stats*` (existentes)

**Step 1: Modificar `wedding_task_stats()`**

```python
# ANTES (task.py:26-31)
@staticmethod
def wedding_task_stats(*, company: Company, wedding: Wedding) -> tuple[int, int]:
    """Return (completed, total) task counts for a wedding."""
    tasks = Task.objects.for_tenant(company).filter(wedding=wedding)
    total = tasks.count()
    completed = tasks.filter(is_completed=True).count()
    return completed, total

# DEPOIS
@staticmethod
def wedding_task_stats(*, company: Company, wedding: Wedding) -> tuple[int, int]:
    """Return (completed, total) task counts for a wedding."""
    from django.db.models import Count, Q

    result = Task.objects.for_tenant(company).filter(
        wedding=wedding
    ).aggregate(
        total=Count("id"),
        completed=Count("id", filter=Q(is_completed=True)),
    )
    return result["completed"], result["total"]
```

Adicionar import no topo (já existe `F, Q`, adicionar `Count`):
```python
from django.db.models import Count, F, Q
```

**Step 2: Verificar que testes passam**

Run: `cd backend && python -m pytest apps/weddings/tests/test_services.py::TestTaskSummaryService::test_wedding_task_stats apps/weddings/tests/test_services.py::TestTaskSummaryService::test_wedding_task_stats_no_tasks -v`
Expected: Ambos passam

**Step 3: Commit**

```bash
git add backend/apps/weddings/services/summaries/task.py
git commit -m "fix(summaries): consolidate wedding_task_stats into single aggregate"
```

---

## Task 3: Fix `wedding_contract_stats()` — 2 queries → 1

**Objective:** Consolidar `exclude(status=CANCELED).count()` + `filter(status=SIGNED).count()` em um único `aggregate()`.

**Files:**
- Modify: `backend/apps/weddings/services/summaries/contract.py:21-28`
- Test: `backend/apps/weddings/tests/test_services.py::TestContractSummaryService::test_wedding_contract_stats*` (existentes)

**Step 1: Modificar `wedding_contract_stats()`**

```python
# ANTES (contract.py:21-28)
@staticmethod
def wedding_contract_stats(
    *, company: Company, wedding: Wedding
) -> tuple[int, int]:
    """Return (signed, total non-canceled) contract counts for a wedding."""
    contracts = Contract.objects.for_tenant(company).filter(wedding=wedding)
    total = contracts.exclude(status=Contract.StatusChoices.CANCELED).count()
    signed = contracts.filter(status=Contract.StatusChoices.SIGNED).count()
    return signed, total

# DEPOIS
@staticmethod
def wedding_contract_stats(
    *, company: Company, wedding: Wedding
) -> tuple[int, int]:
    """Return (signed, total non-canceled) contract counts for a wedding."""
    from django.db.models import Count, Q

    result = Contract.objects.for_tenant(company).filter(
        wedding=wedding
    ).aggregate(
        total=Count("id", filter=~Q(status=Contract.StatusChoices.CANCELED)),
        signed=Count("id", filter=Q(status=Contract.StatusChoices.SIGNED)),
    )
    return result["signed"], result["total"]
```

Adicionar import no topo:
```python
from django.db.models import Count, Q
```

**Step 2: Verificar que testes passam**

Run: `cd backend && python -m pytest apps/weddings/tests/test_services.py::TestContractSummaryService::test_wedding_contract_stats apps/weddings/tests/test_services.py::TestContractSummaryService::test_wedding_contract_stats_no_contracts -v`
Expected: Ambos passam

**Step 3: Commit**

```bash
git add backend/apps/weddings/services/summaries/contract.py
git commit -m "fix(summaries): consolidate wedding_contract_stats into single aggregate"
```

---

## Task 4: Verificação final

**Objective:** Rodar toda a suíte de testes dos summaries para garantir que nada quebrou.

**Step 1: Rodar todos os testes de summaries**

Run: `cd backend && python -m pytest apps/weddings/tests/test_services.py -v --tb=short`
Expected: Todos passam

**Step 2: Rodar testes do dashboard (que consome os summaries)**

Run: `cd backend && python -m pytest apps/weddings/tests/test_apis.py -v --tb=short -k "dashboard"`
Expected: Todos passam

**Step 3: Rodar lint**

Run: `make lint` ou `ruff check .`
Expected: Sem erros novos

---

## Riscos e Mitigações

| Risco | Mitigação |
|---|---|
| `Count("id", filter=Q(...))` pode se comportar diferente de `.filter(...).count()` em queries com JOIN | Não há JOIN nestes casos — são queries simples sobre uma tabela. `Count` com `filter` é equivalente a `.filter().count()` |
| `~Q(status=CANCELED)` pode não ser suportado em todas as versões do Django | Django 3.1+ suporta. O projeto usa Django 5+ |
| `result["count"]` pode ser `None` em queryset vazio | `Count("id")` sempre retorna 0 para queryset vazio, nunca None (diferente de `Sum`) |

## Resultado Esperado

| Métrica | Antes | Depois |
|---|---|---|
| Queries em `overdue_installments()` | 2 | 1 |
| Queries em `wedding_task_stats()` | 2 | 1 |
| Queries em `wedding_contract_stats()` | 2 | 1 |
| Assinatura dos métodos | tuple | tuple (inalterada) |
| Retorno dos métodos | tuple | tuple (inalterada) |
| Total de queries eliminadas | — | 3 queries/summary |
