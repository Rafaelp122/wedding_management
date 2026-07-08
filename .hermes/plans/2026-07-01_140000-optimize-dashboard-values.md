# PR 3 — Otimizar construção de query no dashboard

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Usar `.values()` no `critical_qs` para evitar instanciar 5 objetos `Wedding` — trabalhar com dicts diretamente.

**Architecture:** Queryset com `.values()` antes do slice `[:5]`. Loop itera dicts em vez de model instances.

**Tech Stack:** Django ORM, pytest

---

## Contexto

### Problema

O `critical_qs` no `DashboardService.get_summary()` instancia 5 objetos `Wedding` completos, mas apenas lê 8 campos. Django ORM cria um model instance para cada row, o que inclui:
- Conversão de tipos Python
- Atribuição de `_state`, `_deferred_fields`, etc.
- overhead de memória

Com `.values()`, o ORM retorna dicts puros — zero overhead de model instantiation.

### Código atual

```python
# dashboard_service.py:48-92
critical_qs = (
    Wedding.objects.for_tenant(company)
    .filter(status=Wedding.StatusChoices.IN_PROGRESS, date__lte=ninety_days)
    .annotate(
        incomplete_tasks=Count(...),
        pending_installments=Count(...),
        overdue_tasks=Count(...),
        overdue_installments=Count(...),
    )
    .order_by("date")
)

critical_weddings = []
for w in critical_qs[:5]:                        # ← instancia 5 Wedding objects
    days_until = max(0, (w.date - today).days)    # ← atributo de model instance
    critical_weddings.append({
        "uuid": w.uuid,                            # ← atributo de model instance
        "groom_name": w.groom_name,
        "bride_name": w.bride_name,
        "days_until": days_until,
        "incomplete_tasks": w.incomplete_tasks,    # ← annotated field
        "pending_installments": w.pending_installments,
        "overdue_tasks": w.overdue_tasks,
        "overdue_installments": w.overdue_installments,
    })
```

### Código proposto

```python
critical_qs = (
    Wedding.objects.for_tenant(company)
    .filter(status=Wedding.StatusChoices.IN_PROGRESS, date__lte=ninety_days)
    .annotate(
        incomplete_tasks=Count(...),
        pending_installments=Count(...),
        overdue_tasks=Count(...),
        overdue_installments=Count(...),
    )
    .order_by("date")
    .values(                                    # ← retorna dicts, não instances
        "uuid", "groom_name", "bride_name", "date",
        "incomplete_tasks", "pending_installments",
        "overdue_tasks", "overdue_installments",
    )[:5]

critical_weddings = []
for w in critical_qs:                           # ← w é dict, não model instance
    days_until = max(0, (w["date"] - today).days)  # ← acesso por chave
    critical_weddings.append({
        "uuid": w["uuid"],
        "groom_name": w["groom_name"],
        "bride_name": w["bride_name"],
        "days_until": days_until,
        "incomplete_tasks": w["incomplete_tasks"],
        "pending_installments": w["pending_installments"],
        "overdue_tasks": w["overdue_tasks"],
        "overdue_installments": w["overdue_installments"],
    })
```

### Por que `.values()` funciona aqui

1. **Somente leitura** — o loop não modifica nem persiste os objetos
2. **Campos limitados** — apenas 8 campos de 40+ do model
3. **Campos annoted já são dicts** — `incomplete_tasks` etc. já vêm do `annotate()`
4. **`uuid` é UUIDField** — `.values()` retorna `uuid.UUID` Python puro, serializável

### O que NÃO muda

- Query SQL gerada é **idêntica** — `.values()` apenas muda como o ORM deserializa o resultado
- Retorno de `get_summary()` é **idêntico** — mesmo schema JSON
- Testes existentes cobrem perfeitamente

---

## Arquivos que vão mudar

| Arquivo | Mudança |
|---|---|
| `backend/apps/weddings/services/dashboard_service.py:48-92` | Adicionar `.values()` ao queryset, mudar `w.attr` → `w["attr"]` |

---

## Task 1: Adicionar `.values()` ao `critical_qs`

**Objective:** Evitar instanciação de 5 objetos Wedding usando `.values()`.

**Files:**
- Modify: `backend/apps/weddings/services/dashboard_service.py:48-92`
- Test: `backend/apps/weddings/tests/test_services.py::TestDashboardService` (existentes)

**Step 1: Modificar `critical_qs` e o loop**

Adicionar `.values()` ao queryset e mudar o loop de `w.attr` para `w["attr"]`.

Campos necessários:
- `uuid` — para identificador
- `groom_name`, `bride_name` — nomes
- `date` — para calcular `days_until`
- `incomplete_tasks`, `pending_installments`, `overdue_tasks`, `overdue_installments` — annotations

**Step 2: Verificar que testes passam**

Run: `cd backend && python -m pytest apps/weddings/tests/test_services.py::TestDashboardService -v`
Expected: Todos passam (especialmente `test_get_summary_success`, `test_get_summary_empty_company`)

**Step 3: Commit**

```bash
git add backend/apps/weddings/services/dashboard_service.py
git commit -m "perf(dashboard): use .values() to avoid model instantiation in critical_qs"
```

---

## Task 2: Verificação final

**Objective:** Rodar suíte completa do dashboard e lint.

**Step 1: Rodar todos os testes do dashboard**

Run: `cd backend && python -m pytest apps/weddings/tests/test_services.py::TestDashboardService -v --tb=short`
Expected: Todos passam

**Step 2: Rodar testes de API do dashboard**

Run: `cd backend && python -m pytest apps/weddings/tests/test_apis.py -v --tb=short -k "dashboard"`
Expected: Todos passam

**Step 3: Rodar lint**

Run: `make lint` ou `ruff check .`
Expected: Sem erros novos

---

## Riscos e Mitigações

| Risco | Mitigação |
|---|---|
| `.values()` retorna `uuid.UUID` em vez de string | O JSON serializer do Django Ninja converte `uuid.UUID` para string automaticamente. Testes validam o formato. |
| `.values()` pode quebrar com `select_related` | Não há `select_related` neste queryset — apenas `annotate()` |
| `date` field pode vir como `datetime.date` em vez de `date` | Já é `DateField`, retorna `datetime.date` em ambos os casos. `max(0, (w["date"] - today).days)` funciona normalmente. |

## Resultado Esperado

| Métrica | Antes | Depois |
|---|---|---|
| Objects instanciados no `critical_qs` | 5 Wedding instances | 0 (dicts puros) |
| Memória por row | ~2KB (model overhead) | ~200B (dict) |
| Query SQL gerada | Idêntica | Idêntica |
| Retorno de `get_summary()` | Idêntico | Idêntico |
