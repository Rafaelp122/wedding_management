# Como Comunicar Entre Módulos (Bounded Contexts) com DDD Pragmático

> **Categoria:** Guias & Receitas Práticas (Backend)
> **Relacionados:** [ADR-031: Comunicação Entre Módulos com DDD Pragmático](../../architecture/adr/031-inter-module-communication.md) · [Service Layer Pattern](../../architecture/concepts/service-layer-pattern.md) · [Async Tasks Architecture](../../architecture/concepts/async-tasks-architecture.md)

---

Este guia prático ensina como implementar a comunicação segura e desacoplada entre os diferentes **Bounded Contexts** (módulos) da plataforma, respeitando os contratos arquiteturais garantidos pelo `import-linter`.

---

## 1. As Três Vias de Comunicação Entre Módulos

Para manter o acoplamento baixo e preservar a independência dos modelos internos de cada domínio, a comunicação entre contextos é segregada em três vias formais:

| Necessidade | Mecanismo Arquitetural | Exemplo Real |
| :--- | :--- | :--- |
| **Comando Síncrono / Transacional** | Fachada Pública (`apps.<contexto>.interfaces`) | `ContractService` (logística) criando despesa financeira vinculada via `create_expense_from_contract`. |
| **Efeito Colateral Assíncrono** | Background Task Pós-Commit (`django.tasks`) | `WeddingService.cancel()` enfileirando `on_wedding_canceled_task` para limpar eventos e disparar notificações. |
| **Consulta Analítica Multi-Domínio** | CQRS Reporting (`apps.reporting.selectors.summaries.*`) | Rota de casamentos consultando `WeddingSummarySelector.list_weddings_with_metrics`. |

> [!CAUTION]
> **Regra de Ouro (Inviolável):**
> É **estritamente proibido** importar diretamente arquivos `models.py`, `services.py` ou `managers.py` pertencentes a outro Bounded Context. Toda importação indevida é bloqueada no CI pelo `import-linter`.

---

## 2. Passo a Passo: Criando ou Estendendo uma Fachada Pública (`interfaces.py`)

Quando o módulo `B` precisa fornecer uma operação transacional síncrona para ser consumida pelo módulo `A`, declare a função em `apps/<modulo_b>/interfaces.py`.

### Passo 2.1: Declarar a Função na Fachada

```python
# backend/apps/finances/interfaces.py
from __future__ import annotations

from typing import TYPE_CHECKING
from apps.finances.schemas import ExpenseIn
from apps.finances.services.expense_service import ExpenseService

if TYPE_CHECKING:
    from apps.tenants.models import Company


def create_expense_from_contract(*, company: Company, payload: ExpenseIn) -> str:
    """Cria uma despesa financeira vinculada a um contrato logístico.

    Args:
        company: O tenant corporativo atual.
        payload: Dados validados da despesa (ExpenseIn reutilizado da API Ninja).

    Returns:
        UUID da despesa gerada em formato string.
    """
    expense = ExpenseService.create(company=company, payload=payload)
    return str(expense.uuid)
```

### Passo 2.2: Consumir Exclusivamente via Fachada

No módulo consumidor (`apps/logistics/services/contract_service.py`), importe exclusivamente de `apps.finances.interfaces`:

```python
# backend/apps/logistics/services/contract_service.py
from apps.finances.interfaces import ExpenseIn, create_expense_from_contract

# Execução segura sem importar Expense ou ExpenseService internamente:
create_expense_from_contract(company=company, payload=payload)
```

### Passo 2.3: Atualizar Exceção no `pyproject.toml`

Como a interface consome os serviços internos do próprio módulo, o `import-linter` identifica a travessia transitiva. Autorize a fachada adicionando o caminho em `ignore_imports` no contrato correspondente em `backend/pyproject.toml`:

```toml
[[tool.importlinter.contracts]]
name = "Logistics não pode importar models ou services alheios"
type = "forbidden"
# ...
ignore_imports = [
    "apps.logistics.services.contract_service -> apps.finances.interfaces",
]
```

### Catálogo de Interfaces Públicas Oficiais

| Módulo | Arquivo | Funções Exportadas |
| :--- | :--- | :--- |
| **Finanças** | `apps/finances/interfaces.py` | `create_expense_from_contract` |
| **Logística** | `apps/logistics/interfaces.py` | `get_contract_for_company` |
| **Scheduler** | `apps/scheduler/interfaces.py` | `create_payment_events_for_installments`, `delete_payment_events_for_expense`, `delete_payment_event_for_installment`, `apply_wedding_schedule_template` |
| **Casamentos** | `apps/weddings/interfaces.py` | `get_wedding_display_name` |
| **Notificações** | `apps/notifications/interfaces.py` | `notify_installment_overdue`, `send_notification_async`, `create_notification` |

---

## 3. Passo a Passo: Efeitos Colaterais com Tarefas Assíncronas Coordenadoras

Para efeitos secundários que cruzam domínios (como limpeza de eventos de agenda e envio de e-mails/notificações após o cancelamento de um casamento), utilize tarefas assíncronas disparadas **exclusivamente após o commit da transação**.

### Passo 3.1: Declarar a Tarefa Coordenadora

```python
# backend/apps/weddings/tasks.py
import logging
from django.tasks import task

logger = logging.getLogger(__name__)


@task()
def on_wedding_canceled_task(company_id: int | str, wedding_uuid: str) -> None:
    """Tarefa assíncrona executada após a confirmação do cancelamento de um casamento."""
    from apps.tenants.models import Company
    from apps.weddings.models import Wedding

    company = Company.objects.get(pk=company_id) if isinstance(company_id, int) else Company.objects.get(uuid=company_id)
    wedding = Wedding.objects.for_tenant(company).filter(uuid=wedding_uuid).first()
    if not wedding:
        return

    # Executar limpezas e notificações sem segurar a transação web principal:
    # 1. Cancelar eventos na agenda (scheduler)
    # 2. Despachar notificações transacionais
```

### Passo 3.2: Enfileirar no Hook `transaction.on_commit`

No método de serviço (`WeddingService.cancel`), enfileire a task apenas quando o commit do PostgreSQL tiver sido efetivado:

```python
# backend/apps/weddings/services.py
from django.db import transaction
from apps.weddings.tasks import on_wedding_canceled_task

# Dentro do método de cancelamento sob @transaction.atomic:
instance.cancel()
instance.save()

transaction.on_commit(
    lambda: on_wedding_canceled_task.enqueue(company.id, str(instance.uuid))
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

Sempre que alterar imports ou adicionar novas comunicações entre módulos, execute os quality gates:

```bash
# Executa a verificação estrita de isolamento de Bounded Contexts:
just lint-imports

# Ou via Poe no ambiente uv local do backend:
uv run --project backend poe lint-imports
```

Se algum contrato for quebrado, o `import-linter` exibirá a árvore de rastreamento da dependência proibida:
- Verifique se a operação deve ser migrada para `interfaces.py`.
- Verifique se a query analítica deve residir em `apps/reporting`.
