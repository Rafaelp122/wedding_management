# Regras de Negócio do Domínio de Cronograma (Scheduler) — MOC

> **Categoria:** Regras de Negócio (Domínio de Cronograma / Scheduler)
> **Relacionados:** [MOC Central de Regras de Negócio](../index.md) · [Domínio de Scheduler](../../domains/scheduler-domain.md) · [ADR-030: Rich Domain Model](../../adr/030-rich-domain-model-service-layer.md)

---

## 1. Visão Geral

O subdomínio de **Cronograma e Agendamentos (`scheduler`)** gerencia o calendário de compromissos do casamento (`Event`), o motor de tarefas operacionais (`Task`) e a integração de marcos de planejamento. Suas regras garantem consistência cronológica, detecção inteligente de conflitos de agenda, parametrização de recorrências periódicas e blindagem estrita contra edição manual de eventos contábeis gerados pelo módulo financeiro.

---

## 2. Índice de Notas Atômicas de Regras de Negócio

| Regra / Especificação | Código Canônico | Escopo / Responsabilidade | Entidades Envolvidas |
| :--- | :--- | :--- | :--- |
| **[Proteção Somente-Leitura para Eventos de Pagamento](payment-event-readonly-guard.md)** | `BR-S01` | Blindagem tríplice (criação, edição e deleção manuais bloqueadas) de eventos do tipo `pagamento`, espelhados a partir de parcelas financeiras. | `Event`, `Installment` |
| **[Motor de Regras de Recorrência e Agendamentos](recurrence-rules-engine.md)** | `BR-S02` | Validação de datas futuras, intervalos canônicos de recorrência (`semanal`, `quinzenal`, `mensal`), lembretes preventivos e ciclo de vida de tarefas do checklist. | `Event`, `Task` |
| **[Detecção e Validação de Conflito de Agenda (Soft Overlap)](schedule-conflict-validation.md)** | `BR-S03` | Detecção matemática de colisão de intervalos temporais no mesmo casamento (\((s_1 < e_2) \land (e_1 > s_2)\)) com mecanismo de sobrescrita voluntária (`force_overlap: bool = True`). | `Event`, `Wedding` |

---

## 3. Matriz de Integração e Relações Cruzadas

- **Com o Módulo de Finanças:** Eventos com `event_type = 'pagamento'` são gerados exclusivamente por serviços internos do módulo de finanças via flag `_caller_internal=True`. Veja [Integração de Pagamentos com Agenda](../finances/payment-schedule-integration.md).
- **Com o Módulo de Casamentos:** A criação de novos casamentos com templates canônicos injeta automaticamente eventos e marcos relativos ao evento. Veja [Aplicação de Templates de Cronograma](../weddings/wedding-schedule-templates.md).
- **Com o Módulo de Notificações:** Eventos e tarefas com lembretes ativos disparam notificações contextuais. Veja [Regras de Notificações In-App](../notifications/in-app-notifications-rules.md).
