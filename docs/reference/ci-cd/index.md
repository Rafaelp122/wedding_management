# Especificações Técnicas de CI/CD e Workflows (MOC)

> **Módulo:** [ci-cd](../../architecture/concepts/ci-cd-pipeline-flow.md) | [architecture-standards](../architecture-standards/index.md)
> **Camada:** GitHub Actions Pipelines (`.github/workflows/`)

---

## Visão Geral

As pipelines do **Wedding Management System** são implementadas em workflows reutilizáveis e modulares sob `.github/workflows/`.

Para garantir o princípio de **Notas Atômicas**, a especificação de cada workflow reside em sua respectiva nota técnica de referência:

---

## Especificações Atômicas de Workflows

1. 🧪 **[ci-pr-validation-spec.md](ci-pr-validation-spec.md)**
   Especificação do workflow `ci-pr-validation.yml` (Lint, type-check, Pytest, Vitest, migrations check e smoke test da imagem Docker).

2. 🚀 **[cd-deploy-spec.md](cd-deploy-spec.md)**
   Especificação do workflow `cd-deploy.yml` (Build & Push no Artifact Registry, Migrations no Neon DB, Deploy no Cloud Run e Vercel).

3. 🏗️ **[terraform-pipelines-spec.md](terraform-pipelines-spec.md)**
   Especificação dos workflows de infraestrutura `terraform-ci.yml` e `staging-pipeline.yml` (Validação de 3 roots, planos isolados e opt-in de apply).

4. 🤖 **[ai-code-review-spec.md](ai-code-review-spec.md)**
   Especificação dos workflows de IA `ai-code-review.yml` e `opencode-assistant.yml` (Revisão automática por SHA e assistência interativa em PRs).

---

## Outros Workflows Auxiliares

- **[docs-ci.yml](../../../.github/workflows/docs-ci.yml)** — Executa `make check-docs` em alteração de documentação para prevenir links quebrados.
- **[e2e-tests.yml](../../../.github/workflows/e2e-tests.yml)** — Executa suíte E2E Playwright em Chromium com 2 shards (Consulte [e2e-testing-spec](../testing/e2e-testing-spec.md)).
- **[codeql.yml](../../../.github/workflows/codeql.yml)** — Análise estática de segurança e vulnerabilidades SAST.
