# PR 1 — Fix N+1 queries no domínio financeiro

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Eliminar queries N+1 e consolidar queries redundantes nos services e models do módulo `finances`.

**Architecture:** Manter properties como fallback, mas garantir que hot paths (dashboard, budget list/get) usem anotações `with_total_spent()`. Consolidar queries duplas em `aggregate()` único.

**Tech Stack:** Django ORM, PostgreSQL, pytest, factoryboy

---

## Contexto

### Problemas identificados

| # | Problema | Arquivo | Impacto |
|---|---|---|---|
| 1 | `Budget.total_overall_spent` property dispara `aggregate()` a cada acesso | `models/budget.py:64` | 🔴 N+1 no dashboard |
| 2 | `BudgetCategory.total_spent` property dispara `aggregate()` a cada acesso | `models/budget_category.py:50` | 🔴 N+1 |
| 3 | `budget_percentage_used()` usa a property em vez da anotação | `summaries/financial.py:52` | 🔴 Query extra no dashboard |
| 4 | `ExpenseService.update()` faz 3 queries separadas | `services/expense_service.py:135-155` | 🟡 3 queries → 1 |
| 5 | `InstallmentService.adjust()` faz 2 queries para prev/next | `services/installment_service.py:160-190` | 🟡 2 queries → 1 |

### Padrão existente (correto)

Os schemas já suportam anotações:
```python
# BudgetOut.resolve_total_overall_spent()
val = getattr(obj, "_total_overall_spent", None)
if val is not None:
    return val
return obj.total_overall_spent  # fallback para property
```

Os managers já têm `with_total_spent()`:
```python
# BudgetQuerySet.with_total_spent()
return self.annotate(_total_overall_spent=Coalesce(Sum(...), Decimal("0.00")))
```

### Decisão de design

**Manter as properties** como fallback (para serializers, templates, e uso fora de queryset). **Não remover** — quebraria backward compatibility e é útil para casos isolados.

**Fix real:** Garantir que os hot paths (services que alimentam dashboard e list views) usem `with_total_spent()` antes de acessar a property.

---

## Arquivos que vão mudar

| Arquivo | Mudança |
|---|---|
| `backend/apps/weddings/services/summaries/financial.py` | `budget_percentage_used()` → usar `with_total_spent()` |
| `backend/apps/finances/services/expense_service.py` | `update()` → consolidar 3 queries em 1 `aggregate()` |
| `backend/apps/finances/services/installment_service.py` | `adjust()` → consolidar 2 queries em 1 com `Q` |
| `backend/apps/finances/tests/expenses/test_services.py` | Atualizar testes de `update()` |
| `backend/apps/finances/tests/installments/test_services.py` | Atualizar testes de `adjust()` |

---

## Task 1: Fix `budget_percentage_used()` — usar anotação

**Objective:** Eliminar a query extra causada pela property `total_overall_spent` no dashboard.

**Files:**
- Modify: `backend/apps/weddings/services/summaries/financial.py:48-60`
- Test: `backend/apps/finances/tests/budgets/test_models.py` (existentes devem passar)

**Step 1: Modificar `budget_percentage_used()`**

```python
# ANTES (financial.py:48-60)
@staticmethod
def budget_percentage_used(*, company: Company, wedding: Wedding) -> float:
    try:
        budget = Budget.objects.for_tenant(company).get(wedding=wedding)
        total_spent = budget.total_overall_spent  # ← Query extra!
        total_est = budget.total_estimated
        if total_est > 0:
            pct = float(total_spent) / float(total_est) * 100
            return min(100.0, round(pct, 1))
        return 0.0
    except Budget.DoesNotExist:
        return 0.0

# DEPOIS
@staticmethod
def budget_percentage_used(*, company: Company, wedding: Wedding) -> float:
    try:
        from apps.finances.managers import BudgetQuerySet

        budget = cast(
            BudgetQuerySet,
            Budget.objects.for_tenant(company).with_total_spent(),
        ).get(wedding=wedding)
        total_spent = budget._total_overall_spent
        total_est = budget.total_estimated
        if total_est > 0:
            pct = float(total_spent) / float(total_est) * 100
            return min(100.0, round(pct, 1))
        return 0.0
    except Budget.DoesNotExist:
        return 0.0
```

Adicionar import no topo:
```python
from typing import cast
```

**Step 2: Verificar que testes existentes passam**

Run: `cd backend && python -m pytest apps/finances/tests/budgets/test_models.py -v`
Expected: Todos os testes `TestBudgetTotalOverallSpent` passam (a property continua funcionando)

Run: `cd backend && python -m pytest apps/finances/tests/budgets/test_services.py -v`
Expected: Todos passam

**Step 3: Commit**

```bash
git add backend/apps/weddings/services/summaries/financial.py
git commit -m "fix(finances): use with_total_spent() annotation in budget_percentage_used"
```

---

## Task 2: Consolidar `ExpenseService.update()` — 3 queries → 1

**Objective:** Substituir 3 queries separadas por um único `aggregate()`.

**Files:**
- Modify: `backend/apps/finances/services/expense_service.py:135-155`
- Test: `backend/apps/finances/tests/expenses/test_services.py` (existentes devem passar)

**Step 1: Ler a seção relevante do update**

O bloco problemático está em `ExpenseService.update()`, linhas ~135-155:

```python
if amount_changed and num_installments is None:
    if instance.installments.filter(status="PAID").exists():  # Query 1
        raise BusinessRuleViolation(...)
    InstallmentService.redistribute(
        company=company,
        expense=instance,
        num_installments=instance.installments.count(),  # Query 2
        first_due_date=(
            first_due_date
            or getattr(
                instance.installments.order_by("due_date").first(),  # Query 3
                "due_date",
                date.today(),
            )
        ),
    )
```

**Step 2: Modificar para usar `aggregate()`**

```python
if amount_changed and num_installments is None:
    stats = instance.installments.aggregate(
        has_paid=Count("id", filter=Q(status="PAID")),
        total_count=Count("id"),
        first_due_date=Min("due_date"),
    )

    if stats["has_paid"]:
        raise BusinessRuleViolation(
            detail=(
                "Não é possível alterar o valor total pois existem "
                "parcelas marcadas como pagas. Crie uma nova despesa."
            ),
            code="amount_change_blocked_by_paid",
        )

    InstallmentService.redistribute(
        company=company,
        expense=instance,
        num_installments=stats["total_count"],
        first_due_date=first_due_date or stats["first_due_date"] or date.today(),
    )
```

Adicionar imports no topo do arquivo:
```python
from django.db.models import Count, Min, Q
```

**Step 3: Verificar que testes passam**

Run: `cd backend && python -m pytest apps/finances/tests/expenses/test_services.py::TestExpenseServiceUpdate -v`
Expected: Todos passam (especialmente `test_update_amount_auto_redistribute`, `test_update_amount_blocked_by_paid`)

**Step 4: Commit**

```bash
git add backend/apps/finances/services/expense_service.py
git commit -m "fix(finances): consolidate 3 queries into 1 aggregate in ExpenseService.update"
```

---

## Task 3: Consolidar `InstallmentService.adjust()` — 2 queries → 1

**Objective:** Substituir 2 queries separadas (prev/next) por uma única query com `Q`.

**Files:**
- Modify: `backend/apps/finances/services/installment_service.py:160-190`
- Test: `backend/apps/finances/tests/installments/test_services.py` (existentes devem passar)

**Step 1: Ler a seção relevante do adjust**

O bloco problemático:

```python
if new_due_date:
    prev = (
        Installment.objects.for_tenant(company)
        .filter(
            expense=instance.expense,
            installment_number__lt=instance.installment_number,
        )
        .order_by("-installment_number")
        .first()
    )
    if prev and new_due_date < prev.due_date:
        raise BusinessRuleViolation(...)

    nxt = (
        Installment.objects.for_tenant(company)
        .filter(
            expense=instance.expense,
            installment_number__gt=instance.installment_number,
        )
        .order_by("installment_number")
        .first()
    )
    if nxt and new_due_date > nxt.due_date:
        raise BusinessRuleViolation(...)
```

**Step 2: Modificar para usar `Q` com uma query**

```python
if new_due_date:
    from django.db.models import Q

    neighbors = (
        Installment.objects.for_tenant(company)
        .filter(
            expense=instance.expense,
            Q(installment_number__lt=instance.installment_number)
            | Q(installment_number__gt=instance.installment_number),
        )
        .order_by("installment_number")
    )

    prev = None
    nxt = None
    for inst in neighbors:
        if inst.installment_number < instance.installment_number:
            prev = inst
        else:
            nxt = inst
            break

    if prev and new_due_date < prev.due_date:
        raise BusinessRuleViolation(
            detail=(
                "A data de vencimento não pode ser anterior à "
                f"parcela #{prev.installment_number} ({prev.due_date})."
            ),
            code="due_date_before_previous_installment",
        )

    if nxt and new_due_date > nxt.due_date:
        raise BusinessRuleViolation(
            detail=(
                "A data de vencimento não pode ser posterior à "
                f"parcela #{nxt.installment_number} ({nxt.due_date})."
            ),
            code="due_date_after_next_installment",
        )
```

**Step 3: Verificar que testes passam**

Run: `cd backend && python -m pytest apps/finances/tests/installments/test_services.py::TestInstallmentServiceAdjust -v`
Expected: Todos passam (especialmente `test_adjust_due_date_before_previous`, `test_adjust_due_date_after_next`)

**Step 4: Commit**

```bash
git add backend/apps/finances/services/installment_service.py
git commit -m "fix(finances): consolidate 2 prev/next queries into 1 in InstallmentService.adjust"
```

---

## Task 4: Verificação final

**Objective:** Rodar toda a suíte de testes do módulo finances para garantir que nada quebrou.

**Step 1: Rodar todos os testes de finances**

Run: `cd backend && python -m pytest apps/finances/ -v --tb=short`
Expected: Todos passam

**Step 2: Rodar lint**

Run: `make lint` ou `ruff check .`
Expected: Sem erros novos

**Step 3: Verificar query count (opcional)**

Se tiver `django-debug-toolbar` ou `django-silk`, verificar que o dashboard agora faz menos queries.

---

## Riscos e Mitigações

| Risco | Mitigação |
|---|---|
| `budget_percentage_used` pode ser chamado sem annotation em outro lugar | Property continua existindo como fallback |
| `ExpenseService.update` pode ter edge case com `aggregate` + `Count` | Testes existentes cobrem `amount_change_blocked_by_paid` e `auto_redistribute` |
| `InstallmentService.adjust` pode ter lógica de prev/next quebrada | Testes `test_adjust_due_date_before_previous` e `test_adjust_due_date_after_next` validam |

## Resultado Esperado

| Métrica | Antes | Depois |
|---|---|---|
| Queries no `budget_percentage_used` | 2 (get + aggregate) | 1 (get com annotate) |
| Queries no `ExpenseService.update` (amount change) | 3 | 1 |
| Queries no `InstallmentService.adjust` (com due_date) | 2 | 1 |
| Properties removidas | 0 | 0 (mantidas como fallback) |
