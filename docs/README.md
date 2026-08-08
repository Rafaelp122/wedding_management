# 📚 Documentação Técnica — Wedding Management System

Bem-vindo à documentação técnica oficial do **Wedding Management System**. Nossa documentação segue rigorosamente a metodologia **Diatázis**, dividida em 4 quadrantes conforme o objetivo do leitor:

---

## 🧭 Navegação por Quadrantes (Diatázis Framework)

```text
               APRENDIZADO                       PRÁTICA
        +-----------------------+-----------------------+
        |  1-tutorials/         |  2-how-to/            |
        |  (Onboarding &        |  (Receitas &          |
        |   Primeiros Passos)   |   Troubleshooting)    |
TEORIA  +-----------------------+-----------------------+  PRÁTICA
        |  4-explanation/       |  3-reference/         |
        |  (Arquitetura &       |  (Especificações      |
        |   Regras de Negócio)  |   Técnicas & Models)  |
        +-----------------------+-----------------------+
                COMPREENSÃO                    INFORMAÇÃO
```

---

### 🎓 1. Tutorials (Aprendizado & Onboarding)
Guias práticos passo a passo para novos desenvolvedores:
- [onboarding-quickstart](1-tutorials/onboarding-quickstart.md) — Subindo ambiente local completo (Docker, DB, Backend, Frontend).
- [backend-first-feature](1-tutorials/backend-first-feature.md) — Criando endpoints no Django Ninja + Service Layer.
- [frontend-first-feature](1-tutorials/frontend-first-feature.md) — Criando telas no React + Orval + Zod.
- [gitops-sprint-workflow](1-tutorials/gitops-sprint-workflow.md) — Fluxo de trabalho por Sprints, Branches (`develop`/`main`), Staging e Hotfixes.

---

### 🛠️ 2. How-To Guides (Receitas Práticas do Dev)
Guias focados na solução de problemas e procedimentos do dia a dia:
- **Ambiente Dev:** [setup-local-environment](2-how-to/dev-environment/setup-local-environment.md) | [database-migrations](2-how-to/dev-environment/database-migrations.md)
- **Frontend:** [use-design-md-system](2-how-to/frontend/use-design-md-system.md) | [generate-orval-client](2-how-to/frontend/generate-orval-client.md) | [create-hook-form-zod](2-how-to/frontend/create-hook-form-zod.md) | [msw-testing-patterns](2-how-to/frontend/msw-testing-patterns.md) | [run-playwright-e2e](2-how-to/frontend/run-playwright-e2e.md)
- **Backend:** [run-pytest-suite](2-how-to/backend/run-pytest-suite.md) | [seed-database](2-how-to/backend/seed-database.md) | [mark-overdue-installments](2-how-to/backend/mark-overdue-installments.md) | [register-cron-tasks](2-how-to/backend/register-cron-tasks.md) | [use-core-services](2-how-to/backend/use-core-services.md)

- **Troubleshooting / Ops:** [db-connection-locks](2-how-to/ops-troubleshooting/db-connection-locks.md) | [r2-upload-failures](2-how-to/ops-troubleshooting/r2-upload-failures.md) | [terraform-service-onboarding](2-how-to/ops-troubleshooting/terraform-service-onboarding.md)

---

### 📋 3. Reference (Especificações Técnicas)
Descrições técnicas puras do código, APIs e schemas do banco:
- **APIs e Contratos:** [openapi-schema](3-reference/api/openapi-schema.md) | [error-envelope-spec](3-reference/api/error-envelope-spec.md)
- **Padrões Técnicos:** [commenting-standards](3-reference/architecture-standards/commenting-standards.md) | [testing-standards](3-reference/architecture-standards/testing-standards.md) | [terraform-modules-spec](3-reference/architecture-standards/terraform-modules-spec.md) | [infrastructure-services](3-reference/architecture-standards/infrastructure-services.md)
- **Ambiente:** [environment-variables](3-reference/environment/environment-variables.md)
- **Frontend UI:** [DESIGN.md](../DESIGN.md) | [ui-components-spec](3-reference/frontend/ui-components-spec.md) | [store-state-spec](3-reference/frontend/store-state-spec.md)
- **Entidades de Banco (Models):**
  - [core-models](3-reference/models/core-models.md)
  - [budget-model](3-reference/models/finances/budget-model.md) | [budget-category-model](3-reference/models/finances/budget-category-model.md) | [expense-model](3-reference/models/finances/expense-model.md) | [installment-model](3-reference/models/finances/installment-model.md)
  - [contract-model](3-reference/models/logistics/contract-model.md) | [supplier-model](3-reference/models/logistics/supplier-model.md) | [item-model](3-reference/models/logistics/item-model.md)
  - [event-model](3-reference/models/scheduler/event-model.md) | [task-model](3-reference/models/scheduler/task-model.md)
  - [tenant-model](3-reference/models/tenants/tenant-model.md) | [user-model](3-reference/models/users/user-model.md) | [wedding-model](3-reference/models/weddings/wedding-model.md)

---

### 💡 4. Explanation (Arquitetura & Domínio Fullstack)
Contexto profundo de design, arquitetura e regras de negócio:
- **Visões de Arquitetura & Requisitos:**
  - [requirements](4-explanation/requirements.md) — Matriz de Requisitos Funcionais e Não-Funcionais (RF & RNF).
  - [system-overview](4-explanation/architecture/system-overview.md) — Visão geral da plataforma.
  - [multi-tenancy-strategy](4-explanation/architecture/multi-tenancy-strategy.md) — Estratégia de isolamento multi-tenant.
  - [service-layer-pattern](4-explanation/architecture/service-layer-pattern.md) — Padrão de Service Layer no backend.
  - [smart-dumb-components](4-explanation/architecture/smart-dumb-components.md) — Padrão de componentes no React.
  - [design-system-rationale](4-explanation/architecture/design-system-rationale.md) — Racional de UX, ergonomia e psicologia das cores.
  - [auth-jwt-flow](4-explanation/architecture/auth-jwt-flow.md) — Autenticação JWT e Axios Interceptors.
  - [contract-pdf-upload-r2-flow](4-explanation/architecture/contract-pdf-upload-r2-flow.md) — Upload de contratos em PDF via Cloudflare R2.
  - [ci-cd-pipeline-flow](4-explanation/architecture/ci-cd-pipeline-flow.md) — Fluxo de CI/CD e ownership dos states Terraform.
  - [architectural-guard-rails-suite](4-explanation/architecture/architectural-guard-rails-suite.md) — Suíte de testes de integridade e guard-rails de segurança.
- **Hubs de Domínio Fullstack (MOCs):**
  - [core-domain](4-explanation/domains/core-domain.md) | [dashboard-domain](4-explanation/domains/dashboard-domain.md) | [finances-domain](4-explanation/domains/finances-domain.md) | [logistics-domain](4-explanation/domains/logistics-domain.md) | [scheduler-domain](4-explanation/domains/scheduler-domain.md) | [tenants-domain](4-explanation/domains/tenants-domain.md) | [users-domain](4-explanation/domains/users-domain.md) | [weddings-domain](4-explanation/domains/weddings-domain.md)
- **Regras de Negócio Atômicas:**
  - [installment-overdue-logic](4-explanation/business-rules/finances/installment-overdue-logic.md) | [financial-integrity-rules](4-explanation/business-rules/finances/financial-integrity-rules.md) | [payment-schedule-integration](4-explanation/business-rules/finances/payment-schedule-integration.md) | [budget-category-distribution](4-explanation/business-rules/finances/budget-category-distribution.md)
  - [contract-parent-child-hierarchy](4-explanation/business-rules/logistics/contract-parent-child-hierarchy.md) | [contract-state-machine](4-explanation/business-rules/logistics/contract-state-machine.md) | [cnpj-validation-rules](4-explanation/business-rules/logistics/cnpj-validation-rules.md)
  - [recurrence-rules-engine](4-explanation/business-rules/scheduler/recurrence-rules-engine.md) | [payment-event-readonly-guard](4-explanation/business-rules/scheduler/payment-event-readonly-guard.md) | [wedding-status-lifecycle](4-explanation/business-rules/weddings/wedding-status-lifecycle.md) | [wedding-schedule-templates](4-explanation/business-rules/weddings/wedding-schedule-templates.md)
- **Histórico Arquitetural:**
  - [Índice Completo de ADRs (001-028)](4-explanation/adr/README.md) — Registros de decisões arquiteturais e trade-offs.
