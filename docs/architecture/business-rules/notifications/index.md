# Regras de Negócio do Domínio de Notificações — MOC

> **Categoria:** Regras de Negócio (Domínio de Notificações)
> **Relacionados:** [MOC Central de Regras de Negócio](../index.md) · [Domínio de Notificações](../../domains/notifications-domain.md) · [ADR-017: Infraestrutura de Tarefas Assíncronas](../../adr/017-async-task-infrastructure.md)

---

## 1. Visão Geral

O subdomínio de **Notificações (`notifications`)** fornece o mecanismo transacional e assíncrono de alertas operacionais, avisos e lembretes para usuários da assessoria e noivos. Ele reage a eventos disparados por outros domínios (vencimento iminente de parcelas, atrasos confirmados, compromissos agendados e alterações contratuais), garantindo entrega auditável e marcação atômica de leitura.

---

## 2. Índice de Notas Atômicas de Regras de Negócio

| Regra / Especificação | Código Canônico | Escopo / Responsabilidade | Entidades Envolvidas |
| :--- | :--- | :--- | :--- |
| **[Regras de Negócio de Notificações In-App](in-app-notifications-rules.md)** | `BR-N01` a `BR-N04` | Criação assíncrona desacoplada de notificações, tipos canônicos de alerta (`financial`, `schedule`, `contract`, `system`), controle atômico de leitura individual e em lote (`read_at`), e agregação de contadores para badges na UI. | `Notification`, `NotificationPreference` |

---

## 3. Matriz de Integração e Relações Cruzadas

- **Com o Módulo de Finanças:** Rotinas cron agendadas via Cloud Scheduler disparam a criação de notificações para parcelas que entraram em atraso. Veja [Lógica de Parcelas Vencidas](../finances/installment-overdue-logic.md).
- **Com o Módulo de Cronograma:** Lembretes de eventos configurados com antecedência disparam alertas contextuais. Veja [Motor de Regras de Recorrência](../scheduler/recurrence-rules-engine.md).
