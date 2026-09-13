# Como Disparar e Integrar Notificações In-App (`NotificationService`)

> **Módulo:** [notifications-domain](../../architecture/domains/notifications-domain.md) | [in-app-notifications-rules](../../architecture/business-rules/notifications/in-app-notifications-rules.md)
> **Código:** `backend/apps/notifications/services.py`

---

Este guia prático ensina como integrar o envio de **Notificações In-App** nos serviços do ERP (ex: `finances`, `logistics`, `scheduler`, `weddings`), cobrindo disparos **síncronos** (em tempo real) e **assíncronos** (via tarefas de background `django.tasks`).

---

## 1. Visão Geral do `NotificationService`

O `NotificationService` (`apps.notifications.services.NotificationService`) é o ponto único para criação, listagem e alteração do estado de notificações in-app no backend.

### Métodos Principais:
- **`create_notification`**: Criação síncrona e persistência direta no banco dentro de uma transação.
- **`create_async_notification`**: Enfileiramento assíncrono em segundo plano (ideal para crons e processamentos em lote).
- **`list_notifications`**: Listagem de notificações ativas isolada por empresa (`company`) e usuário (`user`).
- **`get_unread_count`**: Contagem rápida de notificações não lidas.
- **`mark_as_read`** / **`mark_all_as_read`**: Marcação de notificações como lidas.

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

## 4. Categorias, Ancoragem ERP e Deep-Linking

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

## 5. Cuidados e Erros Comuns

> [!WARNING]
> **Incompatibilidade de Tenant (`ValueError`)**:
> Se o `user` informado não pertencer à `company` fornecida, o serviço lançará um `ValueError("Usuário não pertence à empresa informada.")`. Certifique-se de passar usuários vinculados à mesma empresa.

> [!TIP]
> **Validação em Testes Backend**:
> Ao testar a criação de notificações no Pytest, utilize a `NotificationFactory` de `apps.notifications.tests.factories` para montar cenários de teste limpos sem poluir o banco de dados principal.
