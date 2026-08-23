---
title: "Modelo de Casamento"
domain: weddings
type: model-reference
code: backend/apps/weddings/models.py
tests: backend/apps/weddings/tests/test_models.py
---

# Referência do Modelo: Wedding

> **Módulo:** [weddings-domain](../../../architecture/domains/weddings-domain.md) | [wedding-status-lifecycle](../../../architecture/business-rules/weddings/wedding-status-lifecycle.md)
> **Código:** `backend/apps/weddings/models.py`, `backend/apps/weddings/services.py`, `backend/apps/weddings/selectors.py`

---

## Estrutura do Modelo `Wedding`

Herda de `TenantModel` (isolado por `company`).

### Campos:
- `id`: `BigAutoField` (PK).
- `uuid`: `UUIDField` (`unique=True`, `db_index=True`).
- `company`: `ForeignKey` (`tenants.Company`).
- `groom_name`: `CharField(max_length=100)` — Nome do noivo.
- `bride_name`: `CharField(max_length=100)` — Nome da noiva.
- `date`: `DateField` (`validators=[validate_future_date]` na criação/agendamento) — Data do evento.
- `location`: `CharField(max_length=255)` — Local do evento.
- `expected_guests`: `PositiveIntegerField(null=True, blank=True)` — Estimativa de convidados.
- `status`: `CharField(max_length=20, choices=StatusChoices, default='IN_PROGRESS')`:
  - `IN_PROGRESS` ("Em Andamento")
  - `COMPLETED` ("Concluído")
  - `CANCELED` ("Cancelado")
- `template`: `CharField(max_length=50, null=True, blank=True)` — Modelo de cronograma aplicado na criação.

### Índices de Banco de Dados (`Meta.indexes`):
- `models.Index(fields=["company", "status"])` — Otimização de filtro por tenant e status.
- `models.Index(fields=["date"])` — Otimização de ordenação e busca por data.
- `models.Index(fields=["status"])` — Otimização de consultas globais de status.

### Validações do `clean()`:
- O validador `validate_future_date` exige datas futuras no agendamento inicial. O método `clean()` valida o ciclo de vida: impede transição para `COMPLETED` enquanto a data do casamento for futura (`date > hoje`).

---

## Otimizações da Camada de Consulta (`wedding_list_selector`)

Na listagem de casamentos, o seletor `wedding_list_selector()` e o `WeddingQuerySet.with_metrics()` utilizam **`Subquery`** e **`Coalesce`** em vez de `Count(distinct=True)` no Django ORM para anotar o orçamento total (`total_budget`), parcelas atrasadas (`overdue_installments`) e tarefas incompletas (`incomplete_tasks`).

Isso evita o problema de **JOIN Explosion (explosão do produto cartesiano)**, garantindo respostas rápidas da API mesmo em workspaces com centenas de despesas e tarefas.
