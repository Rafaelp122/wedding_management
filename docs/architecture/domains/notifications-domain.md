# Domínio de Notificações & Alertas In-App (Notifications)

> **Categoria:** Domínios de Arquitetura (Bounded Contexts)
> **Relacionados:** [Regras de Notificações In-App](../business-rules/notifications/in-app-notifications-rules.md) · [Arquitetura de Tarefas Assíncronas](../concepts/async-tasks-architecture.md) · [ADR-006: Service Layer](../adr/006-service-layer.md) · [ADR-009: Multi-Tenancy](../adr/009-multitenancy.md) · [ADR-017: Infraestrutura de Tarefas Assíncronas](../adr/017-async-task-infrastructure.md) · [Modelos Base & Padrões Core](../../reference/models/core-models.md)

---

## 1. Visão Geral do Domínio

O domínio de **Notifications** centraliza todo o pipeline de comunicação de eventos, alertas e lembretes gerados pelos módulos operacionais do ERP para os usuários do sistema.

Pilares arquiteturais de notificações:
1. **Comunicação In-App Centralizada:** Persistência de notificações para consumo em tempo real no sino (*notification bell*) da interface web.
2. **Dupla Interface de Criação (Síncrona & Assíncrona):**
   - **Síncrona (`NotificationService.create_notification`):** Para disparos imediatos durante execuções diretas de serviços.
   - **Assíncrona (`dispatch_async_notification_task` via `django.tasks`):** Para disparos disparados por crons ou rotinas pesadas em background (ADR-017).
3. **Isolamento Estrito de Multi-Tenancy:** Cada notificação pertence a uma `Company` e a um `User` destinatário (`user.company_id == company.id`).
4. **Ancoragem Polimórfica Leve:** Associação dinâmica com entidades de negócio (`target_type` e `target_id` UUID), permitindo redirecionamento com clique (*deep link*).

---

## 2. Diagrama ERD e Fluxo de Despacho Assíncrono

```mermaid
erDiagram
    Company ||--o{ Notification : "pertence (CASCADE)"
    User ||--o{ Notification : "destinado a (CASCADE)"

    Notification {
        bigint id PK
        uuid uuid UK "Identificador Público"
        bigint company_id FK "Company (Tenant)"
        bigint user_id FK "User (Destinatário)"
        string title "Título Curto"
        text message "Mensagem do Alerta"
        string type "OVERDUE_INSTALLMENT | UPCOMING_INSTALLMENT | EXPIRING_CONTRACT | TASK_DEADLINE | GENERAL"
        string target_type "installment | expense | task | contract | wedding | general"
        uuid target_id "UUID do Recurso Alvo"
        uuid wedding_id "UUID do Casamento"
        boolean is_read "Status de Leitura"
        datetime read_at "Data da Leitura"
        string link "URL / Rota de Redirecionamento"
        datetime created_at
    }
```

```mermaid
sequenceDiagram
    autonumber
    actor Cron as Cloud Scheduler / Worker
    participant CronService as Celery / Cron Task (Finances)
    participant TaskQueue as django.tasks Engine
    participant NotifTask as dispatch_async_notification_task
    participant NotifSvc as NotificationService
    participant DB as PostgreSQL
    participant Frontend as Frontend React (NotificationBell)

    Cron->>CronService: Dispara varredura diária de parcelas vencidas
    CronService->>TaskQueue: Enfileira dispatch_async_notification_task(...)
    Note over TaskQueue: Desacoplamento não-bloqueante
    TaskQueue->>NotifTask: Executa tarefa assíncrona
    NotifTask->>NotifSvc: NotificationService.create_notification(company, user, ...)
    NotifSvc->>DB: INSERT INTO notifications (is_read=False, ...)
    Frontend->>DB: Polling / GET /api/v1/notifications/
    DB-->>Frontend: Retorna lista de notificações não lidas + Contador
```

---

## 3. Tabela de Entidades, Tipos e Invariantes de Persistência

| Entidade / Componente | Papel Arquitetural | Campos & Tipos | Invariantes de Persistência & Regras de Notificação |
| :--- | :--- | :--- | :--- |
| **`Notification`** | Agregado de Notificação (`BaseModel`) | `company` (`ForeignKey`, `CASCADE`), `user` (`ForeignKey`, `CASCADE`), `title`, `message`, `type` (`NotificationType`), `target_type` (`NotificationTargetType`), `target_id`, `wedding_id`, `is_read`, `read_at`, `link` | **Validação de Tenant (BR-N01):** `user.company_id == company.id` (usuário deve pertencer à empresa informada).<br/>**Índice Composto:** `models.Index(fields=["company", "user", "is_read"])` para lookups rápidos da contagem de não-lidas.<br/>**Transição de Leitura:** Ao marcar como lida, preenche `read_at = timezone.now()`. |
| **`NotificationType`** | Tipos de Eventos do Sistema | `OVERDUE_INSTALLMENT`, `UPCOMING_INSTALLMENT`, `EXPIRING_CONTRACT`, `TASK_DEADLINE`, `CHECKLIST_ITEM_OVERDUE`, `GENERAL` | Categoriza a severidade e o ícone visual a ser renderizado na interface. |
| **`NotificationTargetType`** | Tipos de Entidades Alvo | `installment`, `expense`, `task`, `contract`, `wedding`, `general` | Mapeia o alvo para permitir deep-linking e navegação direta na interface React. |
| **`dispatch_async_notification_task`** | Tarefa em Segundo Plano (`@task()`) | `company_id`, `user_id`, `title`, `message`, `notification_type`, ... | Enfileira a criação da notificação usando `django.tasks` sem bloquear o ciclo de vida da requisição HTTP principal. |

---

## 4. Transclusão de Código Real

### A. Modelo de Dados e Enums de Notificação (`Notification`)
```python
--8<-- "backend/apps/notifications/models.py:27:78"
```

### B. Tarefa Assíncrona de Despacho (`dispatch_async_notification_task`)
```python
--8<-- "backend/apps/notifications/tasks.py:4:54"
```

### C. Serviço de Criação e Validação de Tenant (`NotificationService.create_notification`)
```python
--8<-- "backend/apps/notifications/services.py:43:100"
```

---

## 5. Mapeamento de Camadas (Fullstack)

### Camada de Backend (`backend/apps/notifications/`)
- **Modelos:** `Notification`, `NotificationType`, `NotificationTargetType` em `models.py`.
- **Managers:** `NotificationQuerySet` em `managers.py`.
- **Services:** `NotificationService` em `services.py`.
- **Tasks:** `dispatch_async_notification_task` em `tasks.py`.
- **Selectors:** `notification_list_selector`, `unread_notifications_count_selector` em `selectors.py`.
- **Endpoints:** `api.py` com rotas `GET /notifications/`, `PATCH /notifications/{uuid}/read/`, `POST /notifications/read-all/`.

### Camada de Frontend (`frontend/src/`)
- **Componentes:** `NotificationBell.tsx`, `NotificationPopover.tsx`, `NotificationItem.tsx`.
- **Hooks Customizados:** `useNotifications.ts` (busca periódica com TanStack Query e marcação rápida como lida).

---

## 6. Links e Regras de Negócio Associadas

- [Regras de Negócio de Notificações In-App](../business-rules/notifications/in-app-notifications-rules.md)
- [Arquitetura de Tarefas Assíncronas](../concepts/async-tasks-architecture.md)
- [ADR-006: Service Layer](../adr/006-service-layer.md)
- [ADR-009: Multi-Tenancy](../adr/009-multitenancy.md)
- [ADR-017: Infraestrutura de Tarefas Assíncronas](../adr/017-async-task-infrastructure.md)
- [Modelos Base & Padrões Core](../../reference/models/core-models.md)
- [Core Domain](core-domain.md)
- [Users Domain](users-domain.md)
