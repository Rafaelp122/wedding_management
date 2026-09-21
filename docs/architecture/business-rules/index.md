# Catálogo de Regras de Negócio e Invariantes de Domínio

> **Categoria:** Arquitetura (Regras de Negócio & Invariantes de Domínio)
> **Relacionados:** [Arquitetura & System Design](../index.md) · [Topologia de Domínios](../domains/index.md) · [Índice de ADRs (001–031)](../adr/README.md) · [ADR-030: Rich Domain Model](../adr/030-rich-domain-model-service-layer.md) · [ADR-010: Tolerância Zero](../adr/010-tolerance-zero.md)

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

O catálogo está integrado aos **5 Bounded Contexts operacionais**, cada um dispondo de seu respectivo Hub de Domínio:

<div class="grid cards" markdown>

-   :material-calendar-clock:{ .lg .middle } **[Domínio de Cronograma (Scheduler)](../domains/scheduler-domain.md)**

    ---

    Detecção de conflitos de agenda (soft overlap), blindagem somente-leitura de parcelas financeiras e motor de recorrência periódica.

    [:octicons-arrow-right-24: Acessar Hub do Scheduler](../domains/scheduler-domain.md)

-   :material-cash-multiple:{ .lg .middle } **[Domínio Financeiro (Finances)](../domains/finances-domain.md)**

    ---

    Tolerância zero em parcelas, conservação do teto orçamentário por categoria, máquina de estados de vencimento e benchmark agregado por assessoria.

    [:octicons-arrow-right-24: Acessar Hub de Finanças](../domains/finances-domain.md)

-   :material-truck-delivery:{ .lg .middle } **[Domínio de Logística & Contratos](../domains/logistics-domain.md)**

    ---

    Ciclo de vida contratual com assinatura PDF no Cloudflare R2, hierarquia de termos aditivos e validação estrita de CNPJ.

    [:octicons-arrow-right-24: Acessar Hub de Logística](../domains/logistics-domain.md)

-   :material-bell-ring:{ .lg .middle } **[Domínio de Notificações](../domains/notifications-domain.md)**

    ---

    Alertas transacionais in-app, ciclo de vida de leitura, badges operacionais e integração com rotinas de tarefas assíncronas.

    [:octicons-arrow-right-24: Acessar Hub de Notificações](../domains/notifications-domain.md)

-   :material-heart-multiple:{ .lg .middle } **[Domínio de Casamentos (Weddings)](../domains/weddings-domain.md)**

    ---

    Entidade raiz de planejamento, transições canônicas de ciclo de vida, guarda de conclusão prematura, reabertura de cancelados e templates.

    [:octicons-arrow-right-24: Acessar Hub de Casamentos](../domains/weddings-domain.md)

</div>

---

## 3. Catálogo Canônico Consolidado de Regras de Negócio

### 3.1 Subdomínios Operacionais do Casamento

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

### 3.2 Subdomínios de Plataforma & Inteligência

| Código Canônico | Título da Regra / Invariante | Subdomínio | Hub de Domínio SSOT |
| :--- | :--- | :--- | :--- |
| **BR-C01** | Chaves Híbridas (ID Bigint + UUID v4) | Core | [core-domain.md](../domains/core-domain.md#3-matriz-canonica-de-invariantes-core-ssot) |
| **BR-C02** | Validação Preventiva Compulsória (`full_clean` no `save`) | Core | [core-domain.md](../domains/core-domain.md#3-matriz-canonica-de-invariantes-core-ssot) |
| **BR-C03** | Blindagem Transversal de Casamento (`WeddingOwnedMixin`) | Core | [core-domain.md](../domains/core-domain.md#3-matriz-canonica-de-invariantes-core-ssot) |
| **BR-C04** | Validação Defensiva de Limite de Upload (`MaxFileSizeValidator`) | Core | [core-domain.md](../domains/core-domain.md#3-matriz-canonica-de-invariantes-core-ssot) |
| **BR-T01** | Isolamento Lógico Row-Level Compulsório | Tenants | [tenants-domain.md](../domains/tenants-domain.md#3-matriz-canonica-de-regras-de-tenancy-ssot) |
| **BR-T02** | Geração Determinística de Slug Anti-Colisão | Tenants | [tenants-domain.md](../domains/tenants-domain.md#3-matriz-canonica-de-regras-de-tenancy-ssot) |
| **BR-T03** | Workspace Administrativo Reservado (`admin-workspace`) | Tenants | [tenants-domain.md](../domains/tenants-domain.md#3-matriz-canonica-de-regras-de-tenancy-ssot) |
| **BR-T04** | Propagação Obrigatória de Tenant via `TenantQuerySet.for_tenant()` | Tenants | [tenants-domain.md](../domains/tenants-domain.md#3-matriz-canonica-de-regras-de-tenancy-ssot) |
| **BR-U01** | Normalização e Unicidade Estrita de E-mail | Usuários | [users-domain.md](../domains/users-domain.md#3-matriz-canonica-de-regras-de-identidade-ssot) |
| **BR-U02** | Vínculo Imutável ao Tenant via `on_delete=PROTECT` | Usuários | [users-domain.md](../domains/users-domain.md#3-matriz-canonica-de-regras-de-identidade-ssot) |
| **BR-U03** | Onboarding Atômico de Owner + Empresa | Usuários | [users-domain.md](../domains/users-domain.md#3-matriz-canonica-de-regras-de-identidade-ssot) |
| **BR-U04** | Verificação Preventiva de E-mail para Login | Usuários | [users-domain.md](../domains/users-domain.md#3-matriz-canonica-de-regras-de-identidade-ssot) |
| **BR-U05** | Login Social Google OAuth2 com Auto-Provisionamento | Usuários | [users-domain.md](../domains/users-domain.md#3-matriz-canonica-de-regras-de-identidade-ssot) |
| **BR-D01** | Anti-Data-Stitching em DTOs Agregados | Dashboard | [dashboard-domain.md](../domains/dashboard-domain.md#3-matriz-canonica-de-regras-de-agregacao-ssot) |
| **BR-D02** | Resumo Executivo com Coleções Embutidas | Dashboard | [dashboard-domain.md](../domains/dashboard-domain.md#3-matriz-canonica-de-regras-de-agregacao-ssot) |
| **BR-D03** | Painel de Operações Unificado com LIMIT 5 | Dashboard | [dashboard-domain.md](../domains/dashboard-domain.md#3-matriz-canonica-de-regras-de-agregacao-ssot) |
| **BR-D04** | Séries Temporais Pré-Agregadas em SQL | Dashboard | [dashboard-domain.md](../domains/dashboard-domain.md#3-matriz-canonica-de-regras-de-agregacao-ssot) |
| **BR-R01** | Isolamento de Renderização via DTO Imutável (`WeddingReportDataDTO`) | Relatórios | [reporting-domain.md](../domains/reporting-domain.md#3-matriz-canonica-de-regras-de-relatorios-ssot) |
| **BR-R02** | Identidade Visual e Layout PDF em Dois Passos | Relatórios | [reporting-domain.md](../domains/reporting-domain.md#3-matriz-canonica-de-regras-de-relatorios-ssot) |
| **BR-R03** | Planilha Multi-Aba com Formatação Monetária | Relatórios | [reporting-domain.md](../domains/reporting-domain.md#3-matriz-canonica-de-regras-de-relatorios-ssot) |
| **BR-R04** | Isolamento Multi-Tenant na Extração de Relatórios | Relatórios | [reporting-domain.md](../domains/reporting-domain.md#3-matriz-canonica-de-regras-de-relatorios-ssot) |

---

## 4. Governança e Diretrizes de Manutenção

Toda e qualquer evolução ou refatoração no código de domínio da aplicação deve obedecer às seguintes diretrizes:

- **Paridade Estrita Código-Documentação:** Nenhuma regra de negócio deve ser alterada ou adicionada em `services/`, `models/` ou `selectors/` sem que a respectiva nota atômica seja atualizada em paridade estrita.
- **Formatação Matemática e Visual:** Regras que envolvam fórmulas devem utilizar LaTeX com delimitação `\(...\)` (inline) ou `\[...\]` (bloco), e fluxos de estado devem apresentar diagramas Mermaid (`stateDiagram-v2` ou `flowchart`).
- **Validação Automática de Links:** Toda alteração na documentação deve ser validada localmente através do comando:
  ```bash
  uv run --project backend python scripts/validate_docs_links.py
  ```
