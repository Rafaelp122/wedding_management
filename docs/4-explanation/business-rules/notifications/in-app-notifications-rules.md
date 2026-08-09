# Regras de Negócio: Notificações In-App

> **Módulo:** [notifications-domain](../../domains/notifications-domain.md) | [notification-model](../../../3-reference/models/notifications/notification-model.md)
> **Código:** `backend/apps/notifications/services.py`

---

## 1. Visão Geral

As notificações In-App fornecem alertas em tempo real e em segundo plano para garantir que planejadores e noivos não percam prazos financeiros ou contratuais.

---

## 2. Regras de Negócio (RN-NOTIF)

### RN-NOTIF-01 — Isolamento Estrito por Tenant e Destinatário
Toda notificação é criada obrigatoriamente vinculada a uma empresa (`Company`) e a um usuário (`User`).
- Ao listar notificações ou consultar contagem de pendentes via `list_notifications` ou `get_unread_count`, o ORM aplica estritamente `.for_tenant(company).filter(user=user)`.
- É **PROIBIDO** expor notificações de outro usuário ou de outra empresa.

### RN-NOTIF-02 — Resolução Flexível de Identificadores (PK / UUID / Instâncias)
Para simplificar chamadas síncronas e assíncronas no `NotificationService`:
- Os parâmetros `company` e `user` aceitam tanto objetos instanciados (`Company`, `User`) quanto IDs inteiros ou UUIDs (`str`, `UUID`). O serviço resolve automaticamente a entidade apropriada no banco de dados.

### RN-NOTIF-03 — Disparo Assíncrono sem Bloqueio de Requisição
- Notificações disparadas em background (ex: crons agendadas de parcelas vencidas `mark_overdue_installments`) utilizam `create_async_notification`.
- A função enfileira o job em `dispatch_async_notification_task` usando `django.tasks`, garantindo que o tempo de resposta das requisições síncronas de API não seja afetado.

### RN-NOTIF-04 — Ancoragem de Entidades e Atalhos Inteligentes
- Opcionalmente, a notificação pode receber `target_type` (ex: `installment`, `contract`), `target_id` e `wedding_id` para permitir que a interface frontend exiba atalhos diretos (`link`) para o recurso ERP relevante.

### RN-NOTIF-05 — Estado de Leitura e Auditoria de Timestamps
- Notificações são criadas com `is_read=False` e `read_at=None`.
- Quando um usuário marca uma notificação individual como lida (`mark_as_read`) ou marca todas como lidas (`mark_all_as_read`), o sistema define `is_read=True`, registra `read_at=now()` e atualiza `updated_at=now()`.

### RN-NOTIF-06 — Exclusão Individual e em Lote
- O usuário pode excluir notificações individualmente (`delete_notification`) ou selecionar múltiplas notificações para exclusão em lote (`bulk_delete`).
- As consultas de exclusão filtram estritamente por `company` e `user` (`.for_tenant(company).filter(user=user, uuid__in=ids)`), impedindo que requisições maliciosas alterem registros de outros usuários.

### RN-NOTIF-07 — Apagar Todas com Confirmação Obrigatória
- O botão "Apagar Todas" (`clear_all`) na interface de notificações deve exigir confirmação através de diálogo modal (`ConfirmDeleteDialog`), prevenindo a perda acidental do histórico de notificações.
