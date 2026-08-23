---
title: "Modelo de Notificação In-App"
domain: notifications
type: model-reference
code: backend/apps/notifications/models.py
tests: backend/apps/notifications/tests/test_services.py
---

# Referência do Modelo: Notification

> **Módulo:** [notifications-domain](../../../architecture/domains/notifications-domain.md) | [in-app-notifications-rules](../../../architecture/business-rules/notifications/in-app-notifications-rules.md)
> **Código:** `backend/apps/notifications/models.py`

---

## Estrutura do Modelo `Notification`

O modelo `Notification` herda de `BaseModel` (`apps/core/models.py`), possuindo campos `id`, `uuid`, `created_at` e `updated_at`. Utiliza o gerenciador `TenantManager` para filtragem isolada por empresa.

### Campos

- `id`: BigAutoField (PK)
- `uuid`: UUIDField (unique=True, db_index=True) — Identificador público único.
- `company`: ForeignKey (`tenants.Company`, on_delete=CASCADE, related_name="notifications") — Empresa dona do registro (Tenant).
- `user`: ForeignKey (`users.User`, on_delete=CASCADE, related_name="notifications") — Usuário destinatário.
- `title`: CharField(max_length=255) — Título da notificação.
- `message`: TextField — Conteúdo textual da notificação.
- `type`: CharField(max_length=50, choices=NotificationType.choices, default=GENERAL) — Tipo categórico (`OVERDUE_INSTALLMENT`, `UPCOMING_INSTALLMENT`, `EXPIRING_CONTRACT`, `TASK_DEADLINE`, `CHECKLIST_ITEM_OVERDUE`, `GENERAL`).
- `target_type`: CharField(max_length=50, choices=NotificationTargetType.choices, default="", blank=True) — Tipo de entidade ERP associada (`installment`, `expense`, `task`, `contract`, `wedding`, `general`).
- `target_id`: UUIDField (null=True, blank=True, db_index=True) — UUID do recurso de destino.
- `wedding_id`: UUIDField (null=True, blank=True, db_index=True) — UUID do casamento associado.
- `is_read`: BooleanField (default=False, db_index=True) — Status de leitura.
- `link`: CharField(max_length=500, default="", blank=True) — URL ou rota frontend de atalho.
- `read_at`: DateTimeField (null=True, blank=True) — Timestamp de quando a notificação foi lida.
- `created_at` / `updated_at`: DateTimeField — Timestamps de auditoria.

---

## Schemas e Respostas Ninja API

- `NotificationOut`: Inclui `wedding_name` resolvido dinamicamente sem N+1 queries.
- `BulkNotificationIdsIn`: Aceita `notification_ids: list[UUID4]`.
- `BulkOperationOut`: Retorna `affected_count: int`.

---

## Endpoints da API (`backend/apps/notifications/api.py`)

- `GET /api/v1/notifications/` (`notifications_list`)
- `GET /api/v1/notifications/unread-count/` (`notifications_unread_count`)
- `PATCH /api/v1/notifications/{notification_id}/read/` (`notifications_mark_as_read`)
- `POST /api/v1/notifications/read-all/` (`notifications_mark_all_as_read`)
- `DELETE /api/v1/notifications/{notification_id}/` (`notifications_delete`)
- `POST /api/v1/notifications/bulk-read/` (`notifications_bulk_mark_as_read`)
- `POST /api/v1/notifications/bulk-delete/` (`notifications_bulk_delete`)
- `DELETE /api/v1/notifications/clear-all/` (`notifications_clear_all`)

---

## Enumerações (`TextChoices`)

### `NotificationType`
- `OVERDUE_INSTALLMENT` ("Parcela Vencida")
- `UPCOMING_INSTALLMENT` ("Parcela a Vencer")
- `EXPIRING_CONTRACT` ("Contrato Prestes a Vencer")
- `TASK_DEADLINE` ("Prazo de Tarefa")
- `CHECKLIST_ITEM_OVERDUE` ("Item de Checklist Vencido")
- `GENERAL` ("Geral")

### `NotificationTargetType`
- `installment`, `expense`, `task`, `contract`, `wedding`, `general`

---

## Índices de Desempenho

```python
indexes = [
    models.Index(fields=["company", "user", "is_read"]),
]
```

Permite consultas ultrarrápidas do contador de não-lidas (`unread_count`) e listagem filtrada por usuário e estado de leitura sob multi-tenancy.
