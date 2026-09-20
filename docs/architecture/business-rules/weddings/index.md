# Regras de Negócio do Domínio de Casamentos (Weddings) — MOC

> **Categoria:** Regras de Negócio (Domínio de Casamentos)
> **Relacionados:** [MOC Central de Regras de Negócio](../index.md) · [Domínio de Casamentos](../../domains/weddings-domain.md) · [ADR-030: Rich Domain Model](../../adr/030-rich-domain-model-service-layer.md)

---

## 1. Visão Geral

O subdomínio de **Casamentos (`weddings`)** é a entidade raiz de negócio do sistema. Cada casamento (`Wedding`) aglutina o escopo relacional de orçamento, convidados, contratos, logística e cronograma de um casal. Suas regras regem a máquina de estados do ciclo de vida do evento, a integridade cronológica de datas passadas e futuras, a governança de transições válidas e a automação por templates canônicos de planejamento.

---

## 2. Índice de Notas Atômicas de Regras de Negócio

| Regra / Especificação | Código Canônico | Escopo / Responsabilidade | Entidades Envolvidas |
| :--- | :--- | :--- | :--- |
| **[Ciclo de Vida do Status do Casamento e Validações](wedding-status-lifecycle.md)** | `BR-W01` a `BR-W06` | Máquina de estados do evento (`IN_PROGRESS` $\to$ `COMPLETED` / `CANCELED`), guarda contra conclusão prematura ($d \le d_{\text{today}}$), proteção relacional na exclusão com contratos e despesas ativas, reabertura de cancelados (`wedding.reopen()`) e propriedades dinâmicas de transição em `WeddingOut`. | `Wedding` |
| **[Aplicação de Templates de Cronograma de Casamento](wedding-schedule-templates.md)** | `BR-W07` | Provisionamento automatizado e idempotente de marcos temporais no calendário (`Event`) a partir de templates canônicos relativos à data do casamento (ex.: 12 meses, 6 meses, 3 meses). | `Wedding`, `ScheduleTemplate`, `Event` |

---

## 3. Matriz de Integração e Relações Cruzadas

- **Com o Módulo de Cronograma:** A data do casamento é o ponto de ancoragem para o cálculo de todos os prazos relativos e templates de cronograma. Veja [Aplicação de Templates de Cronograma](wedding-schedule-templates.md).
- **Com o Módulo de Finanças:** Cada casamento possui exatamente um orçamento mestre (`Budget`), que só pode ser instanciado após a criação válida do casamento. Veja [Distribuição e Alocação de Orçamento por Categoria](../finances/budget-category-distribution.md).
- **Com o Módulo de Logística:** Fornecedores e contratos são vinculados estritamente ao casamento, impedindo contaminação cross-wedding. Veja [Hierarquia de Contratos e Aditivos](../logistics/contract-parent-child-hierarchy.md).
