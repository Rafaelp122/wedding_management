# Como Comunicar Entre Módulos (Bounded Contexts) com DDD Pragmático

> **Categoria:** Guias & Receitas Práticas (Backend)
> **Relacionados:** [ADR-031: Comunicação Entre Módulos com DDD Pragmático](../../architecture/adr/031-inter-module-communication.md) · [Service Layer Pattern](../../architecture/concepts/service-layer-pattern.md) · [Async Tasks Architecture](../../architecture/concepts/async-tasks-architecture.md)

---

Este guia prático ensina como implementar a comunicação segura e desacoplada entre os diferentes **Bounded Contexts** (módulos) da plataforma, respeitando os contratos arquiteturais garantidos pelo **Tach**.

---

## 1. As Três Vias de Comunicação Entre Módulos

Para manter o acoplamento baixo e preservar a independência dos modelos internos de cada domínio, a comunicação entre contextos é segregada em três vias formais:

| Necessidade | Mecanismo Arquitetural | Exemplo Real |
| :--- | :--- | :--- |
| **Comando Síncrono / Transacional** | Fachada Pública (`apps.<contexto>.interfaces`) | `ContractService` (contratos) criando despesa financeira vinculada via `create_expense_from_contract`. |
| **Efeito Colateral Assíncrono** | Background Task Pós-Commit (`django.tasks`) | `WeddingService.cancel()` enfileirando `on_wedding_canceled_task` para limpar eventos e disparar notificações. |
| **Consulta Analítica Multi-Domínio** | CQRS Reporting (`apps.reporting.selectors.summaries.*`) | Rota de casamentos consultando `WeddingSummarySelector.list_weddings_with_metrics`. |

> [!CAUTION]
> **Regra de Ouro (Inviolável):**
> É **estritamente proibido** importar diretamente arquivos `models.py`, `services.py` ou `managers.py` pertencentes a outro Bounded Context. Toda importação indevida é bloqueada no CI pelo **Tach** (`tach check`).

---

## 2. Passo a Passo: Criando ou Estendendo uma Fachada Pública (`interfaces.py`)

Quando o módulo `B` precisa fornecer uma operação transacional síncrona para ser consumida pelo módulo `A`, declare a função em `apps/<modulo_b>/interfaces.py`.

### Passo 2.1: Declarar a Função na Fachada

```python
# backend/apps/finances/interfaces.py
from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID
from apps.finances.schemas import ExpenseIn
from apps.finances.services.expense_service import ExpenseService

if TYPE_CHECKING:
    from apps.finances.models import Expense
    from apps.tenants.models import Company


def create_expense_from_contract(
    *,
    company: Company,
    payload: ExpenseIn,
    contract_uuid: UUID | str,
) -> Expense:
    """Cria uma despesa financeira vinculada a um contrato logístico.

    Args:
        company: O tenant corporativo atual.
        payload: Dados validados da despesa (ExpenseIn reutilizado da API Ninja).
        contract_uuid: Identificador único do contrato a ser vinculado.

    Returns:
        A instância de Expense criada e persistida.
    """
    expense_payload = payload.model_copy(update={"contract": contract_uuid})
    return ExpenseService.create(company=company, payload=expense_payload)
```

### Passo 2.2: Consumir Exclusivamente via Fachada

No módulo consumidor (`apps/logistics/services/contract_service.py`), importe exclusivamente de `apps.finances.interfaces`:

```python
# backend/apps/logistics/services/contract_service.py
from apps.finances.interfaces import ExpenseIn, create_expense_from_contract

# Execução segura sem importar Expense ou ExpenseService internamente:
create_expense_from_contract(
    company=company,
    payload=payload,
    contract_uuid=contract.uuid,
)
```

### Passo 2.3: Declarar Dependência no `tach.toml`

Com o **Tach**, a comunicação entre módulos não requer listas frágeis de `ignore_imports`. Basta declarar a dependência explícita no módulo consumidor em `backend/tach.toml` e expor as interfaces na seção `[[interfaces]]`:

```toml
[[modules]]
path = "apps.contracts"
depends_on = [
    # ...
    { path = "apps.finances" },
]

[[interfaces]]
from = ["apps.finances"]
expose = [
    "interfaces.*",
    "schemas.*",
]
```

### Catálogo de Interfaces Públicas Oficiais

| Módulo | Arquivo | Funções Exportadas |
| :--- | :--- | :--- |
| **Finanças** | `apps/finances/interfaces.py` | `create_expense_from_contract`, `create_expense_from_planner_contract`, `add_expense_adjustment_from_addendum` |
| **Contratos** | `apps/contracts/interfaces.py` | `get_contract_for_company`, `list_contracts_for_wedding`, `get_planner_contract_for_wedding`, `get_supplier_for_company`, `enqueue_guest_count_evaluation` |
| **Logística** | `apps/logistics/interfaces.py` | `create_item_for_contract` |
| **Scheduler** | `apps/scheduler/interfaces.py` | `create_payment_events_for_installments`, `delete_payment_events_for_expense`, `delete_payment_event_for_installment`, `apply_wedding_schedule_template`, `enqueue_wedding_checklist_generation` |
| **Casamentos** | `apps/weddings/interfaces.py` | `get_wedding_display_name` |
| **Notificações** | `apps/notifications/interfaces.py` | `notify_installment_overdue`, `send_notification_async`, `create_notification` |
| **Clientes** | `apps/clients/interfaces.py` | `get_client_for_tenant` |

---

## 3. Passo a Passo: Efeitos Colaterais com Tarefas Assíncronas Coordenadoras

Para efeitos secundários que cruzam domínios (como limpeza de eventos de agenda e recálculo de logística após mudança na contagem de convidados), utilize tarefas assíncronas encapsuladas na fachada pública (`interfaces.py`) e disparadas **exclusivamente após o commit da transação**.

### Passo 3.1: Encapsular o Enfileiramento na Fachada do Módulo Dono

```python
# backend/apps/contracts/interfaces.py
from django.db import transaction

def enqueue_guest_count_evaluation(
    *, company_id: int | str, wedding_uuid: str | UUID,
    old_count: int, new_count: int,
) -> None:
    """Enfileira a reavaliação de contratos pós-commit transacional."""
    from apps.contracts.tasks import evaluate_guest_count_impact_task

    transaction.on_commit(
        lambda: evaluate_guest_count_impact_task.enqueue(
            company_id, str(wedding_uuid), old_count, new_count
        )
    )
```

### Passo 3.2: Disparar no Consumidor sem Conhecer a Task Interna

No método de serviço (`WeddingService.update` ou `on_wedding_activated_task`), chame apenas a função da fachada:

```python
# backend/apps/weddings/services.py
from apps.contracts.interfaces import enqueue_guest_count_evaluation

# Dentro do método sob @transaction.atomic:
if guest_count_changed:
    enqueue_guest_count_evaluation(
        company_id=company.id,
        wedding_uuid=instance.uuid,
        old_count=old_guests,
        new_count=new_guests,
    )
```

---

## 4. Passo a Passo: Consultas Analíticas Multi-Domínio (CQRS Reporting)

Evite que managers de domínio façam consultas `SQL Subquery` em tabelas de outros contextos (por exemplo, contar tarefas do `scheduler` ou parcelas de `finances` dentro do `WeddingQuerySet`).

### Onde colocar a consulta?

- **Consultas do próprio agregado:** `apps/<modulo>/managers.py` e `apps/<modulo>/selectors.py`.
- **Consultas analíticas agregadas cross-domain:** `apps/reporting/selectors/summaries/` (ex.: `WeddingSummarySelector`, `ContractSummarySelector`).

### Exemplo de Uso no Controller da API:

```python
# backend/apps/weddings/api.py
from apps.reporting.selectors.summaries.wedding import WeddingSummarySelector

@router.get("/", response=list[WeddingOut], operation_id="weddings_list")
def list_weddings(request: AuthRequest) -> QuerySet[Wedding]:
    # Delegação da leitura analítica ao seletor neutro do Reporting:
    return WeddingSummarySelector.list_weddings_with_metrics(
        company=request.auth.company
    )
```

---

## 5. Como Verificar a Conformidade Arquitetural

Sempre que alterar imports ou adicionar novas comunicações entre módulos, execute os quality gates com o **Tach**:

```bash
# Executa a verificação estrita de isolamento de Bounded Contexts:
just lint-imports
# Ou via alias:
just arch

# Ou via Poe no ambiente uv local do backend:
uv run --project backend poe lint-imports
```

Se algum contrato for quebrado, o `Tach` exibirá o arquivo, linha exata e a fronteira violada:
- Verifique se a operação deve ser migrada para `interfaces.py`.
- Verifique se a query analítica deve residir em `apps/reporting`.
