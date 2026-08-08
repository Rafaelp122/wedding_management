# 🎯 Requisitos Funcionais e Não-Funcionais (Matriz de Rastreabilidade)

> **Módulo:** [system-overview](architecture/system-overview.md)
> **Escopo:** Matriz de Rastreabilidade de Requisitos de Produto e Arquitetura

---

## 1. Visão Geral

Este documento detalha os **Requisitos Funcionais (RF)** e **Não-Funcionais (RNF)** do Wedding Management System, estabelecendo a rastreabilidade direta entre as especificações de produto, as notas atômicas de regras de negócio, a arquitetura e a suíte de testes de integridade.

---

## 2. Requisitos Funcionais (RF)

### 2.1 Módulo Core & Multitenancy
- **RF01 — Isolamento Multitenant de Dados:** O sistema deve garantir que usuários acessem exclusivamente os casamentos e recursos pertencentes à sua empresa (`Company`), bloqueando acessos cross-tenant.
  - 📖 **Rastreabilidade:** [multi-tenancy-strategy](architecture/multi-tenancy-strategy.md) | [tenant-model](../3-reference/models/tenants/tenant-model.md)
  - 🧪 **Teste:** `TestTenantIsolationGuard` em `backend/apps/core/tests/`

- **RF02 — Gestão do Ciclo de Vida do Casamento:** O sistema deve permitir o cadastro, acompanhamento e conclusão de casamentos com controle estrito de status.
  - 📖 **Rastreabilidade:** [wedding-status-lifecycle](business-rules/weddings/wedding-status-lifecycle.md) | [wedding-schedule-templates](business-rules/weddings/wedding-schedule-templates.md)

---

### 2.2 Módulo Financeiro
- **RF03 — Categorias de Orçamento:** O sistema deve permitir organizar gastos em categorias customizáveis com alocação e monitoramento de orçamentos.
  - 📖 **Rastreabilidade:** [budget-category-distribution](business-rules/finances/budget-category-distribution.md) | [budget-model](../3-reference/models/finances/budget-model.md)

- **RF04 — Gestão de Despesas & Ancoragem Contratual:** O sistema deve registrar despesas obrigatórias com vínculos a categorias e contratos legais.
  - 📖 **Rastreabilidade:** [financial-integrity-rules](business-rules/finances/financial-integrity-rules.md) | [expense-model](../3-reference/models/finances/expense-model.md)

- **RF05 — Parcelamento Inteligente com Tolerância Zero:** O sistema deve calcular o parcelamento automático ajustando os centavos de arredondamento na última parcela.
  - 📖 **Rastreabilidade:** [financial-integrity-rules](business-rules/finances/financial-integrity-rules.md) | [installment-overdue-logic](business-rules/finances/installment-overdue-logic.md)

- **RF06 — Controle de Pagamentos & Status Derivado:** O sistema deve derivar dinamicamente o status da despesa (`PENDING` → `PARTIALLY_PAID` → `SETTLED`) e monitorar parcelas `OVERDUE`.
  - 📖 **Rastreabilidade:** [financial-integrity-rules](business-rules/finances/financial-integrity-rules.md) | [installment-model](../3-reference/models/finances/installment-model.md)

- **RF12 — Redistribuição de Parcelas:** O sistema deve permitir alterar o número de parcelas de uma despesa desde que nenhuma parcela esteja marcada como paga.
  - 📖 **Rastreabilidade:** [financial-integrity-rules](business-rules/finances/financial-integrity-rules.md)

---

### 2.3 Módulo Logístico
- **RF07 — Gestão de Fornecedores & Validação CNPJ:** O sistema deve manter cadastro de fornecedores com validação algorítmica de CNPJ, reutilizável entre casamentos.
  - 📖 **Rastreabilidade:** [cnpj-validation-rules](business-rules/logistics/cnpj-validation-rules.md) | [supplier-model](../3-reference/models/logistics/supplier-model.md)

- **RF08 — Máquina de Estados de Contratos & Aditivos:** O sistema deve gerenciar o ciclo de vida do contrato (`DRAFT`, `PENDING`, `SIGNED`, `CANCELED`) e validar a hierarquia de aditivos.
  - 📖 **Rastreabilidade:** [contract-state-machine](business-rules/logistics/contract-state-machine.md) | [contract-parent-child-hierarchy](business-rules/logistics/contract-parent-child-hierarchy.md)

- **RF09 — Upload Seguro de Documentos (R2):** O sistema deve oferecer upload de contratos assinados (PDF) via presigned URLs do Cloudflare R2.
  - 📖 **Rastreabilidade:** [contract-pdf-upload-r2-flow](architecture/contract-pdf-upload-r2-flow.md)

---

### 2.4 Scheduler & Agenda
- **RF10 — Eventos Financeiros Automáticos:** O sistema deve gerar eventos de pagamento na agenda sincronizados com os vencimentos de parcelas.
  - 📖 **Rastreabilidade:** [payment-event-readonly-guard](business-rules/scheduler/payment-event-readonly-guard.md) | [payment-schedule-integration](business-rules/finances/payment-schedule-integration.md)

- **RF11 — Alertas de Vencimento:** O sistema deve notificar o usuário sobre parcelas vencidas e datas limite.
  - 📖 **Rastreabilidade:** [recurrence-rules-engine](business-rules/scheduler/recurrence-rules-engine.md) | [event-model](../3-reference/models/scheduler/event-model.md)

---

## 3. Requisitos Não-Funcionais (RNF)

- **RNF01 — Performance (API < 200ms P50, Dashboard < 500ms):** API REST Django Ninja rápida com rotas estáticas otimizadas.
  - 📖 **Rastreabilidade:** [022-static-routes-for-performance](adr/022-static-routes-for-performance.md) | [system-overview](architecture/system-overview.md)

- **RNF02 — Segurança, JWT Stateless & Privacidade PII:** Autenticação JWT stateless, login social Google OAuth2 e mascaramento de PII em logs de auditoria.
  - 📖 **Rastreabilidade:** [auth-jwt-flow](architecture/auth-jwt-flow.md) | [user-model](../3-reference/models/users/user-model.md)

- **RNF03 — Infraestrutura Cloud Serverless:** Execução em Cloud Run, PostgreSQL Serverless no Neon DB e armazenamento R2.
  - 📖 **Rastreabilidade:** [001-why-cloud-run](adr/001-why-cloud-run.md) | [002-why-neon](adr/002-why-neon.md) | [003-why-r2](adr/003-why-r2.md)

- **RNF04 — Arquitetura Frontend Smart/Dumb & Type-Safety:** Componentes visuais desacoplados da lógica de dados e hooks tipados do Orval.
  - 📖 **Rastreabilidade:** [smart-dumb-components](architecture/smart-dumb-components.md) | [ui-components-spec](../3-reference/frontend/ui-components-spec.md)

- **RNF05 — Auditoria & Testes Automatizados (12 Pilares):** Suíte de testes de guard-rails de segurança e integridade rodando no CI/CD.
  - 📖 **Rastreabilidade:** [architectural-guard-rails-suite](architecture/architectural-guard-rails-suite.md) | [007-hybrid-keys](adr/007-hybrid-keys.md)
