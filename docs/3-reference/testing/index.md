# 🧪 Especificações Técnicas de Testes Automatizados (MOC)

> **Módulo:** [architecture-standards](../architecture-standards/index.md) | [system-overview](../../4-explanation/architecture/system-overview.md) | [ci-cd-pipeline-flow](../../4-explanation/architecture/ci-cd-pipeline-flow.md)
> **Camada:** Backend (`pytest`), Frontend (`Vitest`, `RTL`), E2E (`Playwright`) e IaC (`Terraform`)

---

## Visão Geral

O **Wedding Management System** exige alta cobertura de testes, validação rigorosa de multi-tenancy e integração de qualidade contínua via CI/CD.

Para manter a documentação **atômica, modular e sustentável**, as especificações técnicas de testes são divididas nas seguintes notas de referência:

---

## 📌 Notas Atômicas de Referência

1. 🐍 **[backend-testing-spec.md](backend-testing-spec.md)**
   Padrões de testes no backend usando `pytest`, Model Factories (`apps/*/tests/factories.py`), isolamento de Service Layer, validação de multi-tenancy (HTTP 404) e auditoria de parâmetro `company`.

2. ⚛️ **[frontend-testing-spec.md](frontend-testing-spec.md)**
   Padrões de testes de unidade e integração no frontend usando `Vitest` (`isolate: false`), React Testing Library (RTL), MSW (Mock Service Worker), utilitários em `@/test-utils`, portais do Radix UI e arquitetura Smart vs Dumb.

3. 🎭 **[e2e-testing-spec.md](e2e-testing-spec.md)**
   Padrões de testes de fluxo ponta a ponta (E2E) com `Playwright`, estrutura de Page Object Models (POM), fixtures de autenticação e diretrizes para prevenção de *flaky tests*.

4. 🏗️ **[terraform-testing-spec.md](terraform-testing-spec.md)**
   Padrões de testes unitários declarativos nativos em módulos Terraform (`*.tftest.hcl`), execução em modo `command = plan`, provedores mockados e validação de contratos HCL.

---

## 🛠️ Operational Skills (Playbooks On-Demand)

Além destas notas atômicas de referência, o projeto conta com playbooks operacionais de checklist utilizados pelos agentes durante o desenvolvimento:
- [wedding-backend-testing](../../../.agents/skills/wedding-backend-testing/SKILL.md) — Checklist operacional para testes backend.
- [wedding-frontend-testing](../../../.agents/skills/wedding-frontend-testing/SKILL.md) — Checklist operacional para testes frontend.
