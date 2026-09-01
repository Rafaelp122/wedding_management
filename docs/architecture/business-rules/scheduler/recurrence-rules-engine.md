---
title: "Motor de Regras de Recorrência e Agendamentos"
domain: scheduler
type: business-rule
source_code:
  - backend/apps/scheduler/models/event.py
  - backend/apps/scheduler/models/task.py
  - backend/apps/scheduler/services/events.py
  - backend/apps/scheduler/services/tasks.py
tests:
  - backend/apps/scheduler/tests/appointments/test_models.py
  - backend/apps/scheduler/tests/appointments/test_services.py
  - backend/apps/scheduler/tests/tasks/test_services.py
---

# Motor de Regras de Recorrência e Agendamentos

> **Categoria:** Regra de Negócio (Domínio de Cronograma e Tarefas)
> **Relacionados:** [Proteção Somente-Leitura de Pagamentos](payment-event-readonly-guard.md) · [Templates de Cronograma](../weddings/wedding-schedule-templates.md) · [Integração de Pagamentos com Agenda](../finances/payment-schedule-integration.md) · [Domínio de Scheduler](../../domains/scheduler-domain.md)

---

## 1. Contexto e Invariantes do Domínio

O motor do módulo `scheduler` orquestra dois pilares fundamentais da assessoria de casamentos: **Compromissos de Calendário** (`Event`) e o **Checklist Operacional de Tarefas** (`Task`). O motor garante consistência temporal, parametrização de recorrência periódica e configuração de lembretes preventivos.

### Invariantes Fundamentais:
1. **Regras de Recorrência Parametrizadas (`RecurrenceChoices`):** Eventos suportam frequência definida em português:
   - `none`: Não recorrente (pontual).
   - `semanal`: Recorrência a cada 7 dias ($\Delta t = 7\text{ dias}$).
   - `quinzenal`: Recorrência a cada 14 dias ($\Delta t = 14\text{ dias}$).
   - `mensal`: Recorrência a cada 30 dias / 1 mês ($\Delta t = 30\text{ dias}$).
2. **Invariante de Data Futura na Criação Manual (BR-VAL02):** A data/hora de início (`start_time`) não pode ser anterior à data corrente (`timezone.localdate()`) na criação manual via API (`EventService.create`), disparando `BusinessRuleViolation('event_start_time_in_past')`.
3. **Exceção de Marcos Retroativos (`_allow_historical_start=True`):** Apenas o provisionamento automatizado de templates de casamento (`WeddingService`) pode persistir eventos com datas relativas retroativas.
4. **Motor de Lembretes Preventivos:** Suporta ativação booleana (`reminder_enabled = True`) e antecedência configurável em minutos (`reminder_minutes_before = 60` por padrão).
5. **Checklist e Prazos de Tarefas (`Task`):** As tarefas possuem controle atômico de conclusão (`is_completed = True/False`) e ordenação canônica por pendência e vencimento: `ordering = ["is_completed", "due_date", "created_at"]`.

### Fórmulas Matemáticas de Recorrência e Lembrete:
Para um evento base agendado no instante $t_0$, as ocorrências recorrentes $k \in \{1, 2, \dots\}$ e o instante de disparo do lembrete $t_{\text{reminder}}$ são calculados por:

$$t_k = t_0 + k \cdot \Delta t_{\text{frequência}}, \quad \Delta t \in \{7, 14, 30\}\text{ dias}$$

$$t_{\text{reminder}} = t_0 - \Delta t_{\text{minutos\_antes}}$$

---

## 2. Diagrama de Fluxo e Validação de Agendamento

```mermaid
graph TD
    A["Início: EventService.create"] --> B["1. Validar Tenant & Ownership (ADR-009)"]
    B --> C{"_allow_historical_start == True?"}

    C -->|Sim (Template Engine)| D["Pular checagem de data passada"]
    C -->|Não (Criação Manual)| E{"timezone.localdate(start_time) < timezone.localdate()?"}

    E -->|Sim (Passado)| ERR1["Raise BusinessRuleViolation<br/>('event_start_time_in_past')"]
    E -->|Não| D

    D --> F{"event_type == 'pagamento' e _caller_internal == False?"}
    F -->|Sim (Tentativa Manual)| ERR2["Raise BusinessRuleViolation<br/>('payment_event_readonly')"]
    F -->|Não| G["2. Salvar Evento (full_clean)"]

    G --> H{"reminder_enabled == True?"}
    H -->|Sim| I["Programar notificação para start_time - reminder_minutes_before"]
    H -->|Não| J["Agendamento Concluído"]
    I --> J
```

---

## 3. Matriz de Regras e Casos de Borda

| Código | Regra de Negócio | Gatilho / Condição | Exceção Lançada | Comportamento do Sistema |
| :--- | :--- | :--- | :--- | :--- |
| **BR-S02-A** | **Data Inicial no Futuro** | `start_time` no passado com `_allow_historical_start=False`. | `BusinessRuleViolation` (`event_start_time_in_past`) | Bloqueia agendamento de eventos retroativos na criação manual. |
| **BR-S02-B** | **Edição com Data Passada** | Atualização parcial via `EventService.update` para ajuste histórico. | Nenhuma (Permitido) | Permite reprogramação e correções cadastrais de eventos passados. |
| **BR-S02-C** | **Recorrência Canônica** | Seleção de `recurrence_rule`. | `ValidationError` se fora dos choices | Aplica intervalos padronizados (`semanal`, `quinzenal`, `mensal`). |
| **BR-S02-D** | **Ordenação de Tarefas** | Consulta via `TaskQuerySet`. | Nenhuma | Prioriza tarefas não concluídas (`is_completed=False`) e mais próximas do vencimento. |

---

## 4. Implementação no Código-Fonte Real

### A. Definição do Modelo e Choices de Recorrência (`event.py`)

```python
--8<-- "backend/apps/scheduler/models/event.py:13:61"
```

### B. Validação Cronológica no Serviço de Eventos (`events.py`)

```python
--8<-- "backend/apps/scheduler/services/events.py:64:72"
```

### C. Modelo de Tarefas do Checklist (`task.py`)

```python
--8<-- "backend/apps/scheduler/models/task.py:8:31"
```

---

## 5. Casos de Teste Automatizados (Pytest)

A suíte de testes unitários em `apps/scheduler/tests/appointments/test_models.py`, `apps/scheduler/tests/appointments/test_services.py` e `apps/scheduler/tests/tasks/test_services.py` cobre as regras de recorrência e prazos:

- `test_event_recurrence_rule_choices`: Valida os valores canônicos em PT-BR para `RecurrenceChoices` (`none`, `semanal`, `quinzenal`, `mensal`).
- `test_create_event_rejects_past_start_time`: Valida o bloqueio de início retroativo na criação manual.
- `test_create_historical_template_event_allowed`: Valida permissão de eventos retroativos quando `_allow_historical_start=True`.
- `test_update_event_allows_past_start_time`: Valida permissão de alteração de datas passadas em updates para histórico.
- `test_update_task_toggle_completed`: Valida a transição de estado da tarefa no checklist.
