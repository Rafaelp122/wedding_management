# Regras de Negócio do Domínio Financeiro — MOC

> **Categoria:** Regras de Negócio (Domínio Financeiro)
> **Relacionados:** [MOC Central de Regras de Negócio](../index.md) · [Domínio de Finanças](../../domains/finances-domain.md) · [ADR-010: Tolerância Zero](../../adr/010-tolerance-zero.md) · [ADR-030: Rich Domain Model](../../adr/030-rich-domain-model-service-layer.md)

---

## 1. Visão Geral

O subdomínio de **Finanças (`finances`)** é o núcleo contábil do **Wedding Management System**. Sob a premissa de **Tolerância Zero Centesimal (ADR-010)**, todas as operações com moedas são representadas em `Decimal(12, 2)`, prevenindo perdas ou desvios cumulativos de arredondamento. O domínio engloba orçamentos mestres (`Budget`), categorias com teto compartilhado (`BudgetCategory`), despesas com vínculo jurídico (`Expense`) e parcelas com máquina de estados de liquidação (`Installment`).

---

## 2. Índice de Notas Atômicas de Regras de Negócio

| Regra / Especificação | Código Canônico | Escopo / Responsabilidade | Entidades Envolvidas |
| :--- | :--- | :--- | :--- |
| **[Regras de Integridade Financeira & Tolerância Zero](financial-integrity-rules.md)** | `BR-F01` a `BR-F05` | Conservação centesimal estrita na divisão de parcelas (\(\sum \text{parcelas} \equiv \text{actual\_amount}\)), correspondência exata de valores contratuais, fronteira multi-casamento e imutabilidade de parcelas pagas. | `Expense`, `Installment`, `Contract` |
| **[Distribuição e Alocação de Orçamento por Categoria](budget-category-distribution.md)** | `BR-F04-A` a `BR-F04-D` | Validação de conservação do teto orçamentário global (\(\sum A_k \le T_{\text{estimated}}\)), travas contra condições de corrida (*pessimistic lock* anti-TOCTOU) e proteção contra exclusão de categorias ativas. | `Budget`, `BudgetCategory` |
| **[Lógica de Vencimento e Máquina de Estados de Parcelas](installment-overdue-logic.md)** | `BR-F05-STATUS` | Transições de status de parcelas (`PENDING` $\to$ `PAID` / `OVERDUE`), reconciliação automática de vencimentos via tarefas agendadas OIDC e geração de alertas operacionais. | `Installment`, `Notification` |
| **[Integração de Pagamentos com Agenda de Compromissos](payment-schedule-integration.md)** | `BR-S01-SYNC` | Espelhamento atômico de parcelas financeiras como eventos de calendário do tipo `pagamento`, mantendo sincronização de valores, vencimentos e datas de pagamento. | `Installment`, `Event` |
| **[Benchmark e Média Orçamentária por Assessoria](tenant-budget-benchmark.md)** | `BR-F06` | Padrão CQRS para cálculo analítico em tempo de leitura da média orçamentária da assessoria (\(\mu_{\text{tenant}}\)) e variação percentual relativa (\(\Delta\%\)). | `Budget`, `Company` |

---

## 3. Matriz de Integração e Relações Cruzadas

- **Com o Módulo de Logística:** Despesas podem ser associadas a contratos de fornecedores, exigindo paridade estrita de valores e pertencimento ao mesmo casamento. Veja [Máquina de Estados de Contratos](../logistics/contract-state-machine.md).
- **Com o Módulo de Cronograma:** Toda parcela gerada reflete atômica e automaticamente como um evento no calendário. Veja [Proteção Somente-Leitura para Eventos de Pagamento](../scheduler/payment-event-readonly-guard.md).
- **Com o Módulo de Notificações:** Parcelas que atingem a data de vencimento sem liquidação geram notificações imediatas e transitam para atraso. Veja [Regras de Notificações In-App](../notifications/in-app-notifications-rules.md).
