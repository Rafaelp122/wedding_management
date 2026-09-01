# Requisitos Funcionais e Não-Funcionais (Matriz de Rastreabilidade)

> **Módulo:** [system-overview](concepts/system-overview.md)
> **Escopo:** Matriz de Rastreabilidade de Requisitos de Produto e Arquitetura

---

## 1. Visão Geral

Este documento detalha os **Requisitos Funcionais (RF)** e **Não-Funcionais (RNF)** do Wedding Management System, estabelecendo a rastreabilidade direta entre as especificações de produto, as notas atômicas de regras de negócio, a arquitetura e a suíte de testes de integridade.

---

## 2. Requisitos Funcionais (RF)

### 2.1 Módulo Core & Multitenancy
- **RF01 — Isolamento Multitenant de Dados:** O sistema deve garantir que usuários acessem exclusivamente os casamentos e recursos pertencentes à sua empresa (`Company`), bloqueando acessos cross-tenant.
  - :material-book-open-variant: **Rastreabilidade:** [multi-tenancy-strategy](concepts/multi-tenancy-strategy.md) | [tenants-domain](domains/tenants-domain.md)
  - :material-test-tube: **Teste:** `TestTenantIsolationGuard` em `backend/apps/core/tests/`

- **RF02 — Gestão do Ciclo de Vida do Casamento:** O sistema deve permitir o cadastro, acompanhamento e conclusão de casamentos com controle estrito de status.
  - :material-book-open-variant: **Rastreabilidade:** [wedding-status-lifecycle](business-rules/weddings/wedding-status-lifecycle.md) | [wedding-schedule-templates](business-rules/weddings/wedding-schedule-templates.md)

---

### 2.2 Módulo Financeiro
- **RF03 — Categorias de Orçamento:** O sistema deve permitir organizar gastos em categorias customizáveis com alocação e monitoramento de orçamentos.
  - :material-book-open-variant: **Rastreabilidade:** [budget-category-distribution](business-rules/finances/budget-category-distribution.md) | [finances-domain](domains/finances-domain.md)

- **RF04 — Gestão de Despesas & Ancoragem Contratual:** O sistema deve registrar despesas obrigatórias com vínculos a categorias e contratos legais.
  - :material-book-open-variant: **Rastreabilidade:** [financial-integrity-rules](business-rules/finances/financial-integrity-rules.md) | [finances-domain](domains/finances-domain.md)

- **RF05 — Parcelamento Inteligente com Tolerância Zero:** O sistema deve calcular o parcelamento automático ajustando os centavos de arredondamento na última parcela.
  - :material-book-open-variant: **Rastreabilidade:** [financial-integrity-rules](business-rules/finances/financial-integrity-rules.md) | [installment-overdue-logic](business-rules/finances/installment-overdue-logic.md)

- **RF06 — Controle de Pagamentos & Status Derivado:** O sistema deve derivar dinamicamente o status da despesa (`PENDING` → `PARTIALLY_PAID` → `SETTLED`) e monitorar parcelas `OVERDUE`.
  - :material-book-open-variant: **Rastreabilidade:** [financial-integrity-rules](business-rules/finances/financial-integrity-rules.md) | [finances-domain](domains/finances-domain.md)

- **RF12 — Redistribuição de Parcelas:** O sistema deve permitir alterar o número de parcelas de uma despesa desde que nenhuma parcela esteja marcada como paga.
  - :material-book-open-variant: **Rastreabilidade:** [financial-integrity-rules](business-rules/finances/financial-integrity-rules.md)

---

### 2.3 Módulo Logístico
- **RF07 — Gestão de Fornecedores & Validação CNPJ:** O sistema deve manter cadastro de fornecedores com validação algorítmica de CNPJ, reutilizável entre casamentos.
  - :material-book-open-variant: **Rastreabilidade:** [cnpj-validation-rules](business-rules/logistics/cnpj-validation-rules.md) | [logistics-domain](domains/logistics-domain.md)

- **RF08 — Máquina de Estados de Contratos & Aditivos:** O sistema deve gerenciar o ciclo de vida do contrato (`DRAFT`, `PENDING`, `SIGNED`, `CANCELED`) e validar a hierarquia de aditivos.
  - :material-book-open-variant: **Rastreabilidade:** [contract-state-machine](business-rules/logistics/contract-state-machine.md) | [contract-parent-child-hierarchy](business-rules/logistics/contract-parent-child-hierarchy.md)

- **RF09 — Upload Seguro de Documentos (R2):** O sistema deve oferecer upload de contratos assinados (PDF) via presigned URLs do Cloudflare R2.
  - :material-book-open-variant: **Rastreabilidade:** [contract-pdf-upload-r2-flow](concepts/contract-pdf-upload-r2-flow.md)

---

### 2.4 Scheduler & Agenda
- **RF10 — Eventos Financeiros Automáticos:** O sistema deve gerar eventos de pagamento na agenda sincronizados com os vencimentos de parcelas.
  - :material-book-open-variant: **Rastreabilidade:** [payment-event-readonly-guard](business-rules/scheduler/payment-event-readonly-guard.md) | [payment-schedule-integration](business-rules/finances/payment-schedule-integration.md)

- **RF11 — Alertas de Vencimento:** O sistema deve notificar o usuário sobre parcelas vencidas e datas limite.
  - :material-book-open-variant: **Rastreabilidade:** [recurrence-rules-engine](business-rules/scheduler/recurrence-rules-engine.md) | [scheduler-domain](domains/scheduler-domain.md)

---

## 3. Requisitos Não-Funcionais (RNF)

- **RNF01 — Performance (API < 200ms P50, Dashboard < 500ms):** API REST Django Ninja rápida com rotas estáticas otimizadas.
  - :material-book-open-variant: **Rastreabilidade:** [022-static-routes-for-performance](adr/022-static-routes-for-performance.md) | [system-overview](concepts/system-overview.md)

- **RNF02 — Segurança, JWT Stateless & Privacidade PII:** Autenticação JWT stateless, login social Google OAuth2 e mascaramento de PII em logs de auditoria.
  - :material-book-open-variant: **Rastreabilidade:** [auth-jwt-flow](concepts/auth-jwt-flow.md) | [users-domain](domains/users-domain.md)

- **RNF03 — Infraestrutura Cloud Serverless:** Execução em Cloud Run, PostgreSQL Serverless no Neon DB e armazenamento R2.
  - :material-book-open-variant: **Rastreabilidade:** [001-why-cloud-run](adr/001-why-cloud-run.md) | [002-why-neon](adr/002-why-neon.md) | [003-why-r2](adr/003-why-r2.md)

- **RNF04 — Arquitetura Frontend Smart/Dumb & Type-Safety:** Componentes visuais desacoplados da lógica de dados e hooks tipados do Orval.
  - :material-book-open-variant: **Rastreabilidade:** [smart-dumb-components](concepts/smart-dumb-components.md) | [ui-components-spec](../reference/frontend/ui-components-spec.md)

- **RNF05 — Auditoria & Testes Automatizados (12 Pilares):** Suíte de testes de guard-rails de segurança e integridade rodando no CI/CD.
  - :material-book-open-variant: **Rastreabilidade:** [architectural-guard-rails-suite](concepts/architectural-guard-rails-suite.md) | [007-hybrid-keys](adr/007-hybrid-keys.md)
