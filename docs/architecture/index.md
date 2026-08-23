# Arquitetura e Regras de Negócio (MOC)

Este índice centraliza a visão arquitetural, padrões de engenharia, regras de negócio e registros de decisões arquiteturais (ADRs) do **Wedding Management System**.

---

## 1. Visão Geral e Requisitos

- [requirements](requirements.md) — Matriz de Requisitos Funcionais e Não-Funcionais (RF & RNF).
- [system-overview](concepts/system-overview.md) — Visão geral da plataforma e stack tecnológica.
- [multi-tenancy-strategy](concepts/multi-tenancy-strategy.md) — Estratégia de isolamento multi-tenant por empresa.
- [design-system-rationale](concepts/design-system-rationale.md) — Racional de UX, ergonomia e tokens do Design System.

---

## 2. Padrões de Arquitetura

- [service-layer-pattern](concepts/service-layer-pattern.md) — Padrão de Service Layer no backend (CQRS).
- [query-selectors-pattern](concepts/query-selectors-pattern.md) — Padrão Query Selectors e Custom QuerySets.
- [smart-dumb-components](concepts/smart-dumb-components.md) — Padrão de componentes no React.
- [auth-jwt-flow](concepts/auth-jwt-flow.md) — Autenticação JWT e Axios Interceptors.
- [contract-pdf-upload-r2-flow](concepts/contract-pdf-upload-r2-flow.md) — Upload de contratos em PDF via Cloudflare R2.
- [ci-cd-pipeline-flow](concepts/ci-cd-pipeline-flow.md) — Fluxo de CI/CD e ownership dos states Terraform.
- [architectural-guard-rails-suite](concepts/architectural-guard-rails-suite.md) — Suíte de testes de integridade arquitetural.
- [async-tasks-architecture](concepts/async-tasks-architecture.md) — Arquitetura de tarefas assíncronas e agendamentos.

---

## 3. Domínios da Plataforma

Para a especificação completa dos 10 bounded contexts, consulte o [MOC de Domínios](domains/index.md).

---

## 4. Registros de Decisões Arquiteturais (ADRs)

Para o histórico e trade-offs de todas as decisões tomadas, consulte o [Índice de ADRs (001–028)](adr/README.md).
