# Domínio de Agendamento, Tarefas & Cronograma (Scheduler)

> **Categoria:** Domínios de Arquitetura (Bounded Contexts)
> **Relacionados:** [Motor de Regras de Recorrência](../business-rules/scheduler/recurrence-rules-engine.md) · [Imutabilidade de Eventos de Pagamento](../business-rules/scheduler/payment-event-readonly-guard.md) · [Templates de Cronograma](../business-rules/weddings/wedding-schedule-templates.md) · [Integração Financeiro-Agenda](../business-rules/finances/payment-schedule-integration.md) · [ADR-006: Service Layer](../adr/006-service-layer.md) · [ADR-023: Desacoplamento de Módulos](../adr/023-desacoplamento-modulos-scheduler-finances-weddings.md)

---

## 1. Visão Geral do Domínio

O domínio de **Scheduler** é o coração temporal e operacional do sistema. Ele gerencia a agenda interativa de compromissos (`Event`), o checklist operacional de tarefas do casamento (`Task`), o motor de recorrência periódica e a geração automatizada de cronogramas a partir de modelos pré-configurados (*templates*).

Pilares arquiteturais de agendamento:
1. **Agenda Multimodal:** Suporte a diferentes naturezas de compromissos (`reuniao`, `pagamento`, `visita`, `degustacao`, `outro`) com definição de horários de início e término e alertas configuráveis.
2. **Proteção de Eventos de Pagamento (BR-S01):** Eventos de pagamento vinculados a parcelas financeiras (`source_installment`) são somente leitura no Scheduler. Criação, edição e exclusão desses eventos só podem ser disparadas pela Service Layer de `Finances`.
3. **Trava de Eventos no Passado (BR-S02):** Eventos criados manualmente por usuários não podem possuir data de início anterior ao dia corrente. Apenas a aplicação de templates de casamento permite offsets retroativos (`_allow_historical_start=True`).
4. **Motor de Recorrência:** Eventos podem se repetir em intervalos definidos (`semanal`, `quinzenal`, `mensal`).
5. **Checklist Operacional:** Tarefas com prazos estimados (`due_date`) e alternador de conclusão (`is_completed`).

---

## 2. Diagrama ERD do Domínio Scheduler

```mermaid
erDiagram
    Wedding ||--o{ Event : "agenda (CASCADE)"
    Wedding ||--o{ Task : "contém (CASCADE)"
    Installment |o--o{ Event : "projeta parcela (0..1:N / SET_NULL)"

    Event {
        bigint id PK
        uuid uuid UK "Identificador Público"
        bigint company_id FK "Company"
        bigint wedding_id FK "Wedding"
        bigint source_installment_id FK "Installment (SET_NULL, Read-Only)"
        string title "Título do Compromisso"
        string event_type "reuniao | pagamento | visita | degustacao | outro"
        datetime start_time "Início do Evento"
        datetime end_time "Fim do Evento"
        string recurrence_rule "none | semanal | quinzenal | mensal"
        boolean reminder_enabled "Alerta Ativo"
        integer reminder_minutes_before "Minutos de Antecedência"
        string location "Local"
        text description
    }

    Task {
        bigint id PK
        uuid uuid UK
        bigint company_id FK "Company"
        bigint wedding_id FK "Wedding"
        string title "Título da Tarefa"
        text description
        date due_date "Prazo Limite"
        boolean is_completed "Status de Conclusão"
    }
```

---

## 3. Tabela de Entidades e Invariantes de Persistência

| Entidade | Papel & Relações | Campos & Tipos | Invariantes de Persistência & Regras Temporais |
| :--- | :--- | :--- | :--- |
| **`Event`** | Compromisso na Agenda (`TenantModel`, `WeddingOwnedMixin`) | `wedding` (`ForeignKey`, `CASCADE`), `source_installment` (`ForeignKey`, `SET_NULL`, nullable), `title`, `event_type` (`TypeChoices`), `start_time`, `end_time`, `recurrence_rule`, `reminder_enabled`, `reminder_minutes_before` | **Imutabilidade Financeira (BR-S01):** Eventos com `event_type == 'pagamento'` não podem ser criados, editados ou excluídos diretamente por endpoints do Scheduler.<br/>**Trava de Data (BR-S02):** Na criação manual, `timezone.localdate(start_time) >= timezone.localdate()`.<br/>**Ordenação:** `ordering = ["start_time"]`. |
| **`Task`** | Item do Checklist (`TenantModel`, `WeddingOwnedMixin`) | `wedding` (`ForeignKey`, `CASCADE`), `title`, `description`, `due_date`, `is_completed` (boolean, default False) | **Ordenação Padrão:** `ordering = ["is_completed", "due_date", "created_at"]` (tarefas pendentes e com prazos mais próximos aparecem primeiro). |
| **`EventService`** | Mutação e Validação | `create()`, `update()`, `delete()` | Executa validações em `@transaction.atomic`. Gerencia flags internas `_caller_internal` e `_allow_historical_start`. |
| **`TemplateEngine`** | Geração Automática | `get_template_events()` | Define listas de marcos com `offset_days` relativos à data da cerimônia para inicialização rápida de novos casamentos. |

---

## 4. Transclusão de Código Real

### A. Modelo de Eventos e Regras de Recorrência (`Event`)
```python
--8<-- "backend/apps/scheduler/models/event.py:8:84"
```

### B. Modelo de Tarefas do Checklist (`Task`)
```python
--8<-- "backend/apps/scheduler/models/task.py:8:31"
```

### C. Serviço de Criação com Validação de Data Passada (`EventService.create`)
```python
--8<-- "backend/apps/scheduler/services/events.py:27:72"
```

### D. Especificação de Templates de Cronograma (`templates.py`)
```python
--8<-- "backend/apps/scheduler/services/templates.py:18:58"
```

---

## 5. Mapeamento de Camadas (Fullstack)

### Camada de Backend (`backend/apps/scheduler/`)
- **Modelos:** `Event` (`event.py`), `Task` (`task.py`).
- **Managers:** `EventQuerySet`, `TaskQuerySet` em `managers.py`.
- **Services:** `events.py`, `tasks.py`, `templates.py`.
- **Selectors:** `event_selectors.py`, `task_selectors.py`.
- **Endpoints:** `api.py` com roteadores `/scheduler/events/` e `/scheduler/tasks/`.

### Camada de Frontend (`frontend/src/features/scheduler/`)
- **Páginas & Abas:** `SchedulerPage.tsx`, `SchedulerCalendar.tsx`, `TimelineView.tsx`, `TimelineTable.tsx`, `ChecklistView.tsx`, `ChecklistTable.tsx`.
- **Componentes:** `SchedulerSummaryCards.tsx`, `ReadOnlyEventDetails.tsx`, `CreateEventDialog.tsx`, `EditEventDialog.tsx`.
- **Hooks Customizados:** `useSchedulerPage.ts`, `useTimeline.ts`, `useChecklist.ts`, `useCreateEventForm.ts`, `useEditEventForm.ts`.

---

## 6. Links e Regras de Negócio Associadas

- [Motor de Regras de Recorrência de Eventos](../business-rules/scheduler/recurrence-rules-engine.md)
- [Proteção de Imutabilidade dos Eventos de Pagamento](../business-rules/scheduler/payment-event-readonly-guard.md)
- [Templates de Cronograma do Casamento](../business-rules/weddings/wedding-schedule-templates.md)
- [Integração de Pagamentos com o Cronograma](../business-rules/finances/payment-schedule-integration.md)
- [ADR-006: Service Layer](../adr/006-service-layer.md)
- [ADR-023: Desacoplamento de Módulos](../adr/023-desacoplamento-modulos-scheduler-finances-weddings.md)
- [Modelos Base & Padrões Core](../../reference/models/core-models.md)
- [Finances Domain](finances-domain.md)
