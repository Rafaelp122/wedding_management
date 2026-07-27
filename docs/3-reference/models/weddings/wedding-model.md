# Referência do Modelo: Wedding

> **Módulo:** [weddings-domain](../../../4-explanation/domains/weddings-domain.md) | [wedding-status-lifecycle](../../../4-explanation/business-rules/weddings/wedding-status-lifecycle.md)
> **Código:** `backend/apps/weddings/models.py`, `backend/apps/weddings/services/wedding_service.py`

---

## Estrutura do Modelo `Wedding`

Herda de `TenantModel` (isolado por `company`).

### Campos:
- `id`: `BigAutoField` (PK).
- `uuid`: `UUIDField` (`unique=True`, `db_index=True`).
- `company`: `ForeignKey` (`tenants.Company`).
- `groom_name`: `CharField(max_length=100)` — Nome do noivo.
- `bride_name`: `CharField(max_length=100)` — Nome da noiva.
- `date`: `DateField` (`validators=[validate_future_date]`) — Data do evento.
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
- Impede marcar o status como `COMPLETED` se a `date` do casamento for posterior à data atual (`date > hoje`).

---

## Otimizações da Camada de Serviço (`WeddingService.list`)

Na listagem de casamentos, o `WeddingService.list()` utiliza **`Subquery`** e **`Coalesce`** em vez de `Count(distinct=True)` no Django ORM para anotar o orçamento total (`total_budget`), parcelas atrasadas (`overdue_installments`) e tarefas incompletas (`incomplete_tasks`).

Isso evita o problema de **JOIN Explosion (explosão do produto cartesiano)**, garantindo respostas rápidas da API mesmo em workspaces com centenas de despesas e tarefas.
