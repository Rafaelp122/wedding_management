# Especificação Técnica: Workflows Terraform (`terraform-ci.yml` & `staging-pipeline.yml`)

> **Módulo:** [ci-cd](index.md) | [ci-cd-pipeline-flow](../../4-explanation/architecture/ci-cd-pipeline-flow.md)
> **Workflows:** `.github/workflows/terraform-ci.yml` | `.github/workflows/staging-pipeline.yml`

---

## 1. Visão Geral

Os workflows de infraestrutura gerenciam a validação sintática, planejamento de mudanças HCL e aplicação controlada do Terraform sob os três roots desacoplados (`shared`, `staging`, `production`).

---

## 2. Topologia de Workflows de Infraestrutura

### 2.1 `terraform-ci.yml` (Pull Requests & Production Main)
- **Em Pull Requests**: Valida a sintaxe e formatação (`terraform fmt -check -recursive`), inicializa em modo local sem backend (`init -backend=false`), valida a estrutura (`terraform validate`) nos 3 roots e executa `terraform test` nativo em todos os módulos (`unit_test.tftest.hcl`).
- **Em Push em `main`**: Conecta ao backend GCS via WIF, gera os planos de execução para `shared` e `production`, e salva os artefatos de plano.
- **Opt-in de Apply em Produção**: O comando `terraform apply` só é executado se a variável de repositório `TERRAFORM_PRODUCTION_APPLY_ENABLED` estiver explicitamente definida como `true`.

### 2.2 `staging-pipeline.yml` (Develop Staging)
- **Em Push em `develop`**: Conecta ao backend GCS de staging, gera os planos de execução para `shared` e `staging`, e publica os relatórios de plano no resumo do workflow.
- **Segurança**: Este workflow **NUNCA** executa `terraform apply` automaticamente.

---

## 3. Isolamento e Travas de Segurança

1. **Sem Credenciais em PRs**: Pull Requests nunca recebem permissões GCP OIDC nem acessam os buckets de state no GCS.
2. **State Locking**: Operações remotas utilizam o mecanismo automático de locking do GCS sob o grupo de concorrência `terraform-remote-state`.
3. **Prevent Destroy**: Recursos críticos (Cloud Run, containers Secret Manager, buckets R2) usam `prevent_destroy = true` protegendo contra destruição acidental.
