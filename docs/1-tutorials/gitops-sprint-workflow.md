# Tutorial: Fluxo de Trabalho por Sprints, Branches e GitOps

> **Módulo:** [tutorials](../README.md#🎓-1-tutorials-aprendizado--onboarding)
> **Relacionados:** [onboarding-quickstart](onboarding-quickstart.md) | [ci-cd-pipeline-flow](../4-explanation/architecture/ci-cd-pipeline-flow.md) | [ADR-025](../4-explanation/adr/025-terraform-iac-architecture.md) | [ADR-026](../4-explanation/adr/026-gitops-branching-and-deployment-strategy.md)

---

## 1. Visão Geral

Este tutorial descreve o fluxo de trabalho diário de desenvolvimento por **Sprints**, gerenciamento de **Branches** (`main`, `develop`, `feature/*`, `hotfix/*`, `docs/*`), esteiras de integridade (`integrity-ci.yml`) e deploys automatizados nos ambientes de **Homologação (Staging)** e **Produção** via GitOps com Terraform.

---

## 2. Estrutura de Branches do Projeto

| Branch | Tipo | Finalidade | Ambiente de Deploy |
| :--- | :--- | :--- | :--- |
| **`main`** | Permanente | Código estável de produção usado pelos usuários reais. | **Produção** (`production.tfvars` / Cloud Run + Vercel Prod) |
| **`develop`** | Permanente | Integração das tarefas da Sprint em andamento. | **Homologação** (`staging.tfvars` / Cloud Run Staging + Vercel Staging) |
| **`feature/*`** | Temporária | Desenvolvimento de novas funcionalidades durante a Sprint. | Validação automatizada na esteira `integrity-ci` |
| **`docs/*` / `fix/*`** | Temporária | Correções rápidas isoladas de documentação ou pequenos bugs. | Fast-track na esteira `integrity-ci` |
| **`hotfix/*`** | Temporária | Correções urgentes de bugs em produção. | **Produção** (Merge direto na `main`) |

---

## 3. Como Funciona a Pipeline de Integridade (`integrity-ci`)

A esteira de integridade principal (`integrity-ci.yml`) executa automaticamente nos PRs e pushes tanto da **`develop`** quanto da **`main`**:
- **Filtragem Inteligente de Caminhos (`detect-changes`)**: Se você alterar apenas arquivos na pasta `docs/`, a esteira executa **apenas o `docs-lint`** em 3 segundos, pulando builds e testes pesados de código.
- **Validação de Código (`backend-tests` & `frontend-tests`)**: Executada automaticamente quando há alterações em código Python/React.
- **Sincronização de Contratos (`contract-sync`)**: Valida se as alterações de API no Django Ninja permanecem em sintonia com os hooks do Orval.

---

## 4. Passo a Passo do Desenvolvimento na Sprint

### Passo 1: Iniciar uma Nova Tarefa
Crie uma branch a partir da `develop`:
```bash
git checkout develop
git pull origin develop
git checkout -b feature/nome-da-funcionalidade
```

### Passo 2: Desenvolver e Abrir PR para Homologação
1. Faça os commits seguindo o padrão Conventional Commits (ex: `feat(finances): add monthly chart`).
2. Envie a branch para o GitHub:
   ```bash
   git push -u origin feature/nome-da-funcionalidade
   ```
3. Abra um **Pull Request (PR)** apontando para a branch **`develop`**.

### Passo 3: Merge na `develop` e Deploy Automático em Staging
Ao fazer o merge do PR na branch `develop`:
1. O pipeline [staging-pipeline.yml](../../.github/workflows/staging-pipeline.yml) é ativado.
2. O ambiente de **Homologação** (`wedding-web-app-staging.vercel.app`) é atualizado.
3. Você testa a aplicação no ambiente na nuvem **100% privado** com Login Social do Google e banco isolado.

---

## 5. Finalização da Sprint e Deploy em Produção

Quando todas as tarefas da Sprint estiverem concluídas e testadas em Homologação:

1. Abra um **Pull Request da branch `develop` para a branch `main`**.
2. O Terraform executa o `terraform plan -var-file=environments/production.tfvars` e comenta o plano no PR.
3. A suíte de testes de regressão E2E (Playwright) é executada.
4. Ao aprovar o PR e fazer o merge na **`main`**:
   - A nova versão é implantada em **Produção** automaticamente.

---

## 6. Como Tratar Correções Isoladas e Hotfixes

### Cenário A: Correção rápida de Documentação (`docs/*`)
- Crie a branch `docs/atualiza-guia` a partir da `develop`.
- Abra o PR para `develop` (ou `main`). O job `detect-changes` roda apenas a validação de links em segundos.

### Cenário B: Hotfix Urgente em Produção (`hotfix/*`)
- Crie uma branch a partir da **`main`**:
  ```bash
  git checkout main
  git pull origin main
  git checkout -b hotfix/corrige-login-google
  ```
- Abra o PR apontando direto para a **`main`**.
- Após o merge na `main` (deploy imediato em produção), sincronize a `develop`:
  ```bash
  git checkout develop
  git pull origin develop
  git merge main
  git push origin develop
  ```
