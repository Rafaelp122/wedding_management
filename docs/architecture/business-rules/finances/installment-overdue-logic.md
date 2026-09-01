---
title: "Lógica de Vencimento e Máquina de Estados de Parcelas"
domain: finances
type: business-rule
source_code:
  - backend/apps/finances/services/installment_service.py
  - backend/apps/finances/models/installment.py
  - backend/apps/notifications/services/notification_service.py
tests:
  - backend/apps/finances/tests/installments/test_services.py
---

# Regra de Negócio: Lógica de Vencimento e Máquina de Estados de Parcelas

> **Categoria:** Regra de Negócio (Domínio Financeiro & Automação)
> **Relacionados:** [Tolerância Zero](financial-integrity-rules.md) · [Notificações In-App](../notifications/in-app-notifications-rules.md) · [ADR-005: Cloud Scheduler & OIDC](../../adr/005-oidc-scheduler.md) · [Domínio de Finanças](../../domains/finances-domain.md)

---

## 1. Máquina de Estados da Parcela (`Installment.StatusChoices`)

Cada parcela financeira de uma despesa transita por um ciclo de vida rigoroso baseado em eventos do usuário e rotinas temporais do sistema:

```mermaid
stateDiagram-v2
    [*] --> PENDING: Criação da Despesa / Parcela
    PENDING --> OVERDUE: Cron Diário (due_date < hoje & sem pagamento)
    PENDING --> PAID: InstallmentService.mark_as_paid()
    OVERDUE --> PAID: InstallmentService.mark_as_paid()
    PAID --> PENDING: InstallmentService.unmark_as_paid() (se due_date >= hoje)
    PAID --> OVERDUE: InstallmentService.unmark_as_paid() (se due_date < hoje)
```

---

## 2. Automação de Parcelas Vencidas & Notificações In-App

A transição para o estado `OVERDUE` ocorre diariamente de forma automatizada e serverless:

```mermaid
sequenceDiagram
    autonumber
    participant Sched as GCP Cloud Scheduler
    participant API as Django Ninja Router (Cron API)
    participant Svc as InstallmentService.mark_overdue_installments()
    participant DB as Neon PostgreSQL
    participant Notif as NotificationService

    Sched->>API: POST /api/v1/core/cron/mark-overdue-installments/ (Bearer OIDC Token)
    API->>API: Valida Assinatura do Token OIDC (Google Auth)
    API->>Svc: Executa Varredura de Inadimplência
    Svc->>DB: SELECT * FROM finances_installment WHERE status='PENDING' AND due_date < TODAY
    loop Para cada Parcela Vencida
        Svc->>DB: UPDATE status = 'OVERDUE'
        Svc->>Notif: NotificationService.create_async_notification()
        Notif->>DB: INSERT INTO notifications_notification (Para todos os usuários da Company)
    end
    Svc-->>API: Total de parcelas atualizadas
    API-->>Sched: 200 OK { updated_count: N }
```

---

## 3. Matriz de Transições e Regras Operacionais

| Ação / Transição | Pré-condição | Efeito no Banco | Disparo de Efeitos Colaterais |
| :--- | :--- | :--- | :--- |
| **`mark_as_paid`** | Status atual é `PENDING` ou `OVERDUE`. | Define `status = PAID` e `paid_date = date.today()`. | Dispara `expense.full_clean()` para revalidar a consistência contábil da despesa. |
| **`unmark_as_paid`** | Status atual é `PAID`. | Remove `paid_date` e recalcula status (`OVERDUE` se vencida, `PENDING` se futura). | Revalidação contábil da despesa pai. |
| **`mark_overdue`** | Status é `PENDING` e `due_date < date.today()`. | Define `status = OVERDUE` (`skip_clean=True` para performance em lote). | Cria notificações in-app com link direto para `/weddings/{uuid}?tab=finances`. |
| **`adjust`** | Parcela **NÃO** pode estar `PAID`. | Atualiza `amount` ou `due_date`. | Valida se a nova data não viola a cronologia entre parcelas vizinhas. |

---

## 4. Implementação no Código-Fonte Real

### A. Algoritmo de Varredura e Notificação (`installment_service.py`)

```python
--8<-- "backend/apps/finances/services/installment_service.py:559:630"
```

### B. Marcação e Reversão de Pagamento (`installment_service.py`)

```python
--8<-- "backend/apps/finances/services/installment_service.py:305:354"
```

---

## 5. Casos de Teste Automatizados (Pytest)

- `test_mark_overdue_installments_updates_pending_and_notifies`: Valida atualização para `OVERDUE` e geração de notificação in-app para usuários da empresa.
- `test_mark_as_paid_sets_paid_date_and_status`: Valida transição para `PAID` e atribuição da data atual.
- `test_unmark_as_paid_restores_overdue_if_past_due_date`: Valida restauração correta do status para `OVERDUE` quando a data de vencimento já passou.
