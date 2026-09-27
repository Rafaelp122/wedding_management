# Como Disparar e Integrar Notificações In-App (`NotificationService`)

> **Categoria:** Guia Prático (Backend & Notificações)
> **Relacionados:** [Domínio de Notificações](../../architecture/domains/notifications-domain.md) · [Regras de Notificações In-App](../../architecture/business-rules/notifications/in-app-notifications-rules.md) · [ADR-006: Service Layer e CQRS](../../architecture/adr/006-service-layer.md) · [Como Criar Background Tasks](create-background-tasks.md) · [Query Selectors Customizados](create-query-selectors.md)

---

Este guia prático ensina como integrar o envio de **Notificações In-App** nos serviços do ERP (ex: `finances`, `logistics`, `scheduler`, `weddings`), cobrindo disparos **síncronos** (em tempo real) e **assíncronos** (via tarefas de background `django.tasks`), além de como realizar consultas segregadas via seletores CQRS.

---

## 1. Visão Geral do `NotificationService`

O `NotificationService` (`apps.notifications.services.NotificationService`) é responsável **exclusivamente por operações de mutação** (criação, despacho assíncrono e alteração de estado) de notificações in-app no backend, garantindo isolamento multitenant.

### Métodos Principais de Mutação:
- **`create_notification`**: Criação síncrona e persistência direta no banco dentro de uma transação.
- **`create_async_notification`**: Enfileiramento assíncrono em segundo plano via `django.tasks` (ideal para crons e processamentos em lote).
- **`mark_as_read`** / **`mark_all_as_read`**: Marcação de notificações individuais ou em lote como lidas.
- **`bulk_mark_as_read`** / **`bulk_delete`** / **`clear_all`**: Operações de mutação em massa e limpeza.

> [!IMPORTANT]
> **Segregação CQRS (ADR-006):**
> Em conformidade estrita com o padrão CQRS e a ADR-006, o `NotificationService` **NÃO possui métodos de leitura ou consulta**. Operações de listagem e contagem são de responsabilidade estrita dos seletores em `apps.notifications.selectors` (`notification_list_selector`, `notification_unread_count_selector`).

---

## 2. Como Disparar Notificações Síncronas

Use `NotificationService.create_notification` quando a notificação deve ser persistida imediatamente durante a execução da requisição ou método do serviço.

### Exemplo: Notificando ao Atualizar um Contrato

```python
from apps.notifications.models import NotificationTargetType, NotificationType
from apps.notifications.services import NotificationService

# Dentro do seu serviço de domínio (ex: ContractService)
NotificationService.create_notification(
    company=contract.company,
    user=contract.wedding.user,
    title="Contrato Atualizado",
    message=f"O contrato '{contract.name}' teve seu status alterado.",
    notification_type=NotificationType.EXPIRING_CONTRACT,
    link=f"/weddings/{contract.wedding.uuid}?tab=vendors&contract_id={contract.uuid}",
    target_type=NotificationTargetType.CONTRACT,
    target_id=contract.uuid,
    wedding_id=contract.wedding.uuid,
)
```

> [!NOTE]
> **Resolução Flexível de Identificadores**: Os parâmetros `company` e `user` aceitam instâncias do modelo (`Company`, `User`), IDs inteiros (`int`) ou UUIDs (`str` / `UUID`).

---

## 3. Como Disparar Notificações Assíncronas (Background Tasks)

Em crons de verificação em massa ou rotinas agendadas (ex: verificação noturna de parcelas vencidas), **NÃO bloqueie a execução síncrona**. Utilizar `NotificationService.create_async_notification` enfileira o job em `django.tasks`.

### Exemplo: Disparando em uma Tarefa Agendada

```python
from apps.notifications.models import NotificationTargetType, NotificationType
from apps.notifications.services import NotificationService

# Em um serviço de cron ou tarefa agendada
for user in active_users:
    NotificationService.create_async_notification(
        company=user.company_id,
        user=user.id,
        title="Prazo de Tarefa Próximo",
        message="Você possui tarefas com vencimento para hoje.",
        notification_type=NotificationType.TASK_DEADLINE,
        target_type=NotificationTargetType.TASK,
        wedding_id=wedding.uuid,
    )
```

---

## 4. Consultas e Seletores CQRS (`selectors.py`)

As consultas de notificações não passam pelo `NotificationService`. Toda leitura é centralizada em `apps.notifications.selectors`:

### Seletores Disponíveis:
- **`notification_list_selector(*, company, user, unread_only=False)`**: Retorna um `NotificationQuerySet` encadeável anotado com `wedding_name` e ordenado cronologicamente (`recent()`), com suporte ao filtro de apenas não lidas.
- **`notification_unread_count_selector(*, company, user)`**: Retorna a contagem inteira de notificações pendentes (`is_read=False`) do usuário no tenant.
- **`notification_get_selector(*, company, user, uuid)`**: Recupera uma notificação específica validando tenant e destinatário.

### Exemplo de Uso no Controller da API:

```python
from apps.notifications.selectors import (
    notification_list_selector,
    notification_unread_count_selector,
)

# Na rota GET /api/v1/notifications/
@notifications_router.get("/", response=list[NotificationOut], operation_id="notifications_list")
@paginate
def list_notifications(request: AuthRequest, is_read: bool | None = None):
    return notification_list_selector(
        company=request.user.company,
        user=request.user,
        unread_only=(is_read is False),
    )

# Na rota GET /api/v1/notifications/unread-count/
@notifications_router.get("/unread-count/", response=UnreadCountOut, operation_id="notifications_unread_count")
def get_unread_count(request: AuthRequest) -> UnreadCountOut:
    count = notification_unread_count_selector(company=request.user.company, user=request.user)
    return UnreadCountOut(count=count)
```

---

## 5. Categorias, Ancoragem ERP e Deep-Linking

Ao criar uma notificação, passe os enums e parâmetros corretos para garantir a melhor experiência no frontend:

### `NotificationType`
- `OVERDUE_INSTALLMENT`: Parcela vencida (Ícone: :material-alert: Alerta).
- `UPCOMING_INSTALLMENT`: Parcela a vencer (Ícone: :material-clock-outline: Relógio).
- `EXPIRING_CONTRACT`: Contrato prestes a vencer (Ícone: :material-file-document-outline: Documento).
- `TASK_DEADLINE`: Prazo de tarefa (Ícone: :material-clock-outline: Relógio).
- `CHECKLIST_ITEM_OVERDUE`: Item de checklist vencido (Ícone: :material-alert: Alerta).
- `GENERAL`: Alerta geral (Ícone: :material-bell-outline: Sino).

### `NotificationTargetType`
- `installment`, `expense`, `task`, `contract`, `wedding`, `general`.

### Padrão de Links (`link`)
Monte links frontend com parâmetros de busca (*query params*) para ativar abas e focar o recurso desejado:
```python
# Link para focar em uma parcela no painel financeiro
link=f"/weddings/{wedding_uuid}?tab=finances&expense_id={expense_uuid}"
```

---

## 6. Cuidados e Erros Comuns

> [!WARNING]
> **Incompatibilidade de Tenant (`BusinessRuleViolation`)**:
> Se o `user` informado não pertencer à `company` fornecida, o serviço lançará um `BusinessRuleViolation("Usuário não pertence à empresa informada.")`. Certifique-se de passar usuários vinculados à mesma empresa.

> [!TIP]
> **Validação em Testes Backend**:
> Ao testar a criação de notificações no Pytest, utilize a `NotificationFactory` de `apps.notifications.tests.factories` para montar cenários de teste limpos sem poluir o banco de dados principal.
