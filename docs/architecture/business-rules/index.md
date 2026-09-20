# Catálogo de Regras de Negócio e Invariantes de Domínio (MOC Geral)

> **Categoria:** Arquitetura (Regras de Negócio & Invariantes de Domínio)
> **Relacionados:** [Arquitetura & System Design](../index.md) · [MOC de Domínios](../domains/index.md) · [Índice de ADRs (001–031)](../adr/README.md) · [ADR-030: Rich Domain Model](../adr/030-rich-domain-model-service-layer.md) · [ADR-010: Tolerância Zero](../adr/010-tolerance-zero.md)

---

## 1. Visão Geral e Filosofia de Engenharia

O **Wedding Management System** opera sob o princípio da **Fonte Única da Verdade (Single Source of Truth - SSOT)** para todas as regras de negócio e invariantes de domínio. Em conformidade com a metodologia de **Notas Atômicas (ADR-028)** e o padrão **Rich Domain Model (ADR-030)**, cada comportamento intrínseco, cálculo matemático, restrição temporal e máquina de estados é formalizado em sua respectiva nota atômica dentro deste diretório.

### Pilares Fundamentais de Governança de Negócio:
1. **Validação em 3 Níveis Formais (ADR-030):**
   - *Nível 1 (Entrada / Sintaxe)*: Pydantic Schemas (`schemas/`) validam tipos, formatos, strings e coerência sintática imediata (Fail-Fast com HTTP 422).
   - *Nível 2 (Invariantes de Domínio)*: Modelos Django (`models/`) encapsulam validações de integridade no método `clean()` (invocado compulsoriamente pelo `BaseModel.save()`) e máquinas de estado ricas.
   - *Nível 3 (Caso de Uso / Orquestração)*: Serviços (`services/`) orquestram transações atômicas (`@transaction.atomic`), regras multi-entidade, isolamento multi-tenant (`company`) e efeitos colaterais.
2. **Tolerância Zero Contábil (ADR-010):** Tratamento rigoroso de valores monetários utilizando `Decimal(12, 2)`, conservação de centavos na divisão de parcelas e impedimento de desvios cumulativos de arredondamento.
3. **Isolamento de Bounded Contexts (ADR-031):** Comunicação entre contextos segregada por interfaces explícitas e tarefas assíncronas coordenadas.

---

## 2. Estrutura dos 5 Subdomínios de Negócio

O catálogo está particionado em **5 subdomínios operacionais**, cada um dispondo de seu respectivo Map of Content (MOC):

<div class="grid cards" markdown>

-   :material-calendar-clock:{ .lg .middle } **[Domínio de Cronograma (Scheduler)](scheduler/index.md)**

    ---

    Detecção de conflitos de agenda (soft overlap), blindagem somente-leitura de parcelas financeiras e motor de recorrência periódica.

    [:octicons-arrow-right-24: Acessar MOC do Scheduler](scheduler/index.md)

-   :material-cash-multiple:{ .lg .middle } **[Domínio Financeiro (Finances)](finances/index.md)**

    ---

    Tolerância zero em parcelas, conservação do teto orçamentário por categoria, máquina de estados de vencimento e benchmark agregado por assessoria.

    [:octicons-arrow-right-24: Acessar MOC de Finanças](finances/index.md)

-   :material-truck-delivery:{ .lg .middle } **[Domínio de Logística & Contratos](logistics/index.md)**

    ---

    Ciclo de vida contratual com assinatura PDF no Cloudflare R2, hierarquia de termos aditivos e validação estrita de CNPJ.

    [:octicons-arrow-right-24: Acessar MOC de Logística](logistics/index.md)

-   :material-bell-ring:{ .lg .middle } **[Domínio de Notificações](notifications/index.md)**

    ---

    Alertas transacionais in-app, ciclo de vida de leitura, badges operacionais e integração com rotinas de tarefas assíncronas.

    [:octicons-arrow-right-24: Acessar MOC de Notificações](notifications/index.md)

-   :material-heart-multiple:{ .lg .middle } **[Domínio de Casamentos (Weddings)](weddings/index.md)**

    ---

    Entidade raiz de planejamento, transições canônicas de ciclo de vida, guarda de conclusão prematura, reabertura de cancelados e templates.

    [:octicons-arrow-right-24: Acessar MOC de Casamentos](weddings/index.md)

</div>

---

## 3. Catálogo Canônico Consolidado de Regras de Negócio

| Código Canônico | Título da Regra de Negócio | Subdomínio | Nota Atômica SSOT |
| :--- | :--- | :--- | :--- |
| **BR-W01** | Conclusão Prematura Bloqueada | Casamentos | [wedding-status-lifecycle.md](weddings/wedding-status-lifecycle.md) |
| **BR-W02** | Data Inicial no Futuro | Casamentos | [wedding-status-lifecycle.md](weddings/wedding-status-lifecycle.md) |
| **BR-W03** | Proteção Relacional na Exclusão | Casamentos | [wedding-status-lifecycle.md](weddings/wedding-status-lifecycle.md) |
| **BR-W04** | Ordenação Decrescente de Casamentos | Casamentos | [wedding-status-lifecycle.md](weddings/wedding-status-lifecycle.md) |
| **BR-W05** | Transição Ilegal de Status do Casamento | Casamentos | [wedding-status-lifecycle.md](weddings/wedding-status-lifecycle.md) |
| **BR-W06** | Reabertura de Casamento Cancelado | Casamentos | [wedding-status-lifecycle.md](weddings/wedding-status-lifecycle.md) |
| **BR-W07** | Templates Canônicos de Cronograma | Casamentos | [wedding-schedule-templates.md](weddings/wedding-schedule-templates.md) |
| **BR-F01** | Tolerância Zero Centesimal de Parcelas | Finanças | [financial-integrity-rules.md](finances/financial-integrity-rules.md) |
| **BR-F02** | Conformidade Financeira com Contrato | Finanças | [financial-integrity-rules.md](finances/financial-integrity-rules.md) |
| **BR-F03** | Fronteira Cross-Wedding Guard Financeiro | Finanças | [financial-integrity-rules.md](finances/financial-integrity-rules.md) |
| **BR-F04-A..D** | Distribuição e Teto Orçamentário por Categoria | Finanças | [budget-category-distribution.md](finances/budget-category-distribution.md) |
| **BR-F05** | Vencimento e Máquina de Estados de Parcelas | Finanças | [installment-overdue-logic.md](finances/installment-overdue-logic.md) |
| **BR-F06** | Benchmark e Média Orçamentária por Assessoria | Finanças | [tenant-budget-benchmark.md](finances/tenant-budget-benchmark.md) |
| **BR-L01** | Máquina de Estados e Assinatura de Contratos | Logística | [contract-state-machine.md](logistics/contract-state-machine.md) |
| **BR-L02** | Hierarquia Pai-Filho e Termos Aditivos | Logística | [contract-parent-child-hierarchy.md](logistics/contract-parent-child-hierarchy.md) |
| **BR-L03** | Compartilhamento Multi-Casamento de Fornecedores | Logística | [contract-state-machine.md](logistics/contract-state-machine.md) |
| **BR-L04** | Desacoplamento de Aquisição e Pagamento de Itens | Logística | [contract-state-machine.md](logistics/contract-state-machine.md) |
| **BR-L05** | Validação e Sanitização de CNPJ (Módulo 11) | Logística | [cnpj-validation-rules.md](logistics/cnpj-validation-rules.md) |
| **BR-S01** | Proteção Somente-Leitura de Eventos de Pagamento | Cronograma | [payment-event-readonly-guard.md](scheduler/payment-event-readonly-guard.md) |
| **BR-S02** | Motor de Regras de Recorrência e Agendamento | Cronograma | [recurrence-rules-engine.md](scheduler/recurrence-rules-engine.md) |
| **BR-S03** | Detecção de Conflito de Agenda (Soft Overlap) | Cronograma | [schedule-conflict-validation.md](scheduler/schedule-conflict-validation.md) |
| **BR-N01..04** | Ciclo de Vida e Leitura de Notificações In-App | Notificações | [in-app-notifications-rules.md](notifications/in-app-notifications-rules.md) |

---

## 4. Governança e Diretrizes de Manutenção

Toda e qualquer evolução ou refatoração no código de domínio da aplicação deve obedecer às seguintes diretrizes:

- **Paridade Estrita Código-Documentação:** Nenhuma regra de negócio deve ser alterada ou adicionada em `services/`, `models/` ou `selectors/` sem que a respectiva nota atômica seja atualizada em paridade estrita.
- **Formatação Matemática e Visual:** Regras que envolvam fórmulas devem utilizar LaTeX com delimitação `\(...\)` (inline) ou `\[...\]` (bloco), e fluxos de estado devem apresentar diagramas Mermaid (`stateDiagram-v2` ou `flowchart`).
- **Validação Automática de Links:** Toda alteração na documentação deve ser validada localmente através do comando:
  ```bash
  uv run --project backend python scripts/validate_docs_links.py
  ```
