---
title: "Arquitetura e Fluxo da Pipeline GitOps (CI/CD & IaC)"
domain: architecture
type: concept
source_code:
  - justfile
  - .github/workflows/ci-pr-validation.yml
  - .github/workflows/cd-deploy.yml
  - terraform/shared/main.tf
  - terraform/staging/main.tf
  - terraform/production/main.tf
tests:
  - backend/apps/core/tests/
  - terraform/
---

# Arquitetura e Fluxo da Pipeline GitOps (CI/CD & IaC)

> **Categoria:** Conceito Arquitetural
> **Relacionados:** [ADR-025: Terraform e GitOps Multi-Cloud](../adr/025-terraform-iac-architecture.md) · [ADR-026: Estratégia de Branches e Deploy](../adr/026-gitops-branching-and-deployment-strategy.md) · [ADR-027: Topologia de States do Terraform](../adr/027-terraform-state-topology.md) · [ADR-029: Modern Task Runner (Just)](../adr/029-modern-task-runner-just.md) · [Índice de CI/CD](../../reference/ci-cd/index.md) · [Índice de Testes](../../reference/testing/index.md)

---

## 1. Visão Geral e Princípios GitOps

O **Wedding Management System** implementa uma arquitetura automatizada de **GitOps e CI/CD** onde o repositório Git é a única fonte da verdade (*Single Source of Truth*) para código-fonte, infraestrutura em nuvem e banco de dados.

### Quatro Pilares de Separação de Responsabilidade:
1. **CI (Validação Estrita em PRs):** Executada de forma hermética e isolada, sem credenciais de nuvem com privilégios de escrita nem acesso aos backends remotos de produção.
2. **CD (Entrega Contínua da Aplicação):** Publica imagens de container no Google Artifact Registry, roda migrações de banco no Neon DB e atualiza Cloud Run e Vercel apenas após merge nas branches protegidas (`develop` e `main`).
3. **IaC (Infraestrutura Declarativa com Terraform):** Gerencia 3 roots totalmente isolados (`shared`, `staging`, `production`), com arquivos de estado (*statefiles*) separados em buckets GCS dedicados para blindar o raio de impacto (*blast radius*).
4. **Paridade Local/Remota:** O comando local `just check-ci` executa exatamente os mesmos linters, checagens estáticas e testes que rodam no GitHub Actions.

---

## 2. Diagrama Fullstack do Fluxo GitOps & Deploy

```mermaid
flowchart TD
    subgraph DEV_FLOW["1. Desenvolvimento & PR"]
        DEV_LOCAL["Desenvolvedor (just check-ci)"] -->|Git Push| PR["Pull Request (develop / main)"]
        PR --> CI_GATE["GitHub Actions: ci-pr-validation.yml"]
        CI_GATE --> LINT["Lint & Mypy (Ruff/Types)"]
        CI_GATE --> TESTS["Testes (Pytest + Vitest)"]
        CI_GATE --> DOCS["Docs Check (just check-docs)"]
        CI_GATE --> TF_CHECK["Terraform (fmt, validate, tftest)"]
    end

    subgraph STAGING_DEPLOY["2. Homologação (Branch develop)"]
        MERGE_DEV["Merge em develop"] --> CD_STG["cd-deploy.yml (Staging)"]
        CD_STG --> DOCKER_STG["Build & Push Docker (Artifact Registry)"]
        DOCKER_STG --> MIGRATE_STG["Aplica Migrations (Neon DB Staging)"]
        MIGRATE_STG --> CLOUD_RUN_STG["Deploy Cloud Run Staging"]
        CLOUD_RUN_STG --> VERCEL_PREVIEW["Deploy Frontend Preview (Vercel)"]
        MERGE_DEV --> TF_PLAN_STG["Terraform Plan (shared + staging)"]
    end

    subgraph PROD_DEPLOY["3. Produção (Branch main)"]
        MERGE_MAIN["Merge em main"] --> CD_PROD["cd-deploy.yml (Production)"]
        CD_PROD --> DOCKER_PROD["Build & Push Docker (Artifact Registry)"]
        DOCKER_PROD --> MIGRATE_PROD["Aplica Migrations (Neon DB Prod)"]
        MIGRATE_PROD --> CLOUD_RUN_PROD["Deploy Cloud Run Production"]
        CLOUD_RUN_PROD --> VERCEL_PROD["Deploy Frontend Production (Vercel)"]
        MERGE_MAIN --> TF_PLAN_PROD["Terraform Plan (shared + production)"]
        TF_PLAN_PROD -->|Aprovação Explícita (opt-in)| TF_APPLY_PROD["Terraform Apply"]
    end

    CI_GATE -->|Todos os Gates Aprovados| MERGE_DEV
    CI_GATE -->|Todos os Gates Aprovados| MERGE_MAIN
```

---

## 3. Topologia de States do Terraform (ADR-027)

Para mitigar qualquer risco de alterações acidentais afetarem recursos produtivos, o repositório divide a infraestrutura em **3 roots independentes**:

```text
terraform/
├── shared/       # Artefatos globais (GCP Artifact Registry, DNS, IAM base)
├── staging/      # Ambiente de homologação (Cloud Run Staging, Cloud Scheduler Staging)
└── production/   # Ambiente produtivo (Cloud Run Prod, Cloud Scheduler Prod)
```

- Cada root possui seu próprio bucket GCS de state (`backend "gcs"`).
- O root `staging` nunca referencia nem pode sobrescrever recursos do root `production`.

---

## 4. Gates de Qualidade no `justfile`

O `justfile` centraliza todos os comandos de validação local para evitar discrepâncias entre o ambiente de desenvolvimento e o CI:

```just
--8<-- "justfile:170:178"
```

---

## 5. Matriz Técnica de Workflows do GitHub Actions

| Workflow | Foco Principal | Gatilho | Especificação Técnica |
| :--- | :--- | :--- | :--- |
| **`ci-pr-validation.yml`** | Lint, tipos, Pytest, Vitest, Docs, Terraform | Pull Requests para `develop` / `main` | [ci-pr-validation-spec](../../reference/ci-cd/ci-pr-validation-spec.md) |
| **`cd-deploy.yml`** | Docker Build, Neon Migrations, Cloud Run, Vercel | Pushes / Merges em `develop` e `main` | [cd-deploy-spec](../../reference/ci-cd/cd-deploy-spec.md) |
| **`terraform-ci.yml`** | Validação sintática e `terraform test` | Alterações em `terraform/**` | [terraform-pipelines-spec](../../reference/ci-cd/terraform-pipelines-spec.md) |
| **`e2e-tests.yml`** | Testes ponta-a-ponta distribuídos em shards | Pushes em branches principais | [e2e-testing-spec](../../reference/testing/e2e-testing-spec.md) |
| **`ai-code-review.yml`** | Auditoria automática de conformidade arquitetural | Pull Requests | [ai-code-review-spec](../../reference/ci-cd/ai-code-review-spec.md) |
