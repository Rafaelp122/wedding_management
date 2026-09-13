# Tutorial: Fluxo de Trabalho por Sprints, Branches e GitOps

> **Módulo:** [tutorials](../index.md)
> **Relacionados:** [onboarding-quickstart](onboarding-quickstart.md) | [ci-cd-pipeline-flow](../architecture/concepts/ci-cd-pipeline-flow.md) | [ADR-025](../architecture/adr/025-terraform-iac-architecture.md) | [ADR-026](../architecture/adr/026-gitops-branching-and-deployment-strategy.md)

---

## 1. Entenda as Branches e os Ambientes

| Branch | Uso | Resultado após o merge |
|:---|:---|:---|
| `main` | Código estável | CI aprovada chama o CD no Environment `Production`; Terraform planeja `shared` e `production`, com apply condicionado ao opt-in. |
| `develop` | Integração da Sprint | CI aprovada chama o CD no Environment `Preview`; Terraform planeja `shared` e `staging`, sem aplicar. |
| `feature/*`, `fix/*`, `docs/*` | Trabalho da Sprint, criado a partir de `develop` | Apenas validação no PR; nenhum deploy. |
| `hotfix/*` | Correção urgente, criada a partir de `main` | Apenas validação no PR; o deploy ocorre depois do merge em `main`. |

Os Environments `Preview` e `Production` armazenam somente identificadores e versões de secrets do GCP, além das configurações de cada destino. Os valores de `DATABASE_URL` e `SECRET_KEY` permanecem no Secret Manager.

---

## 2. Abra um PR para `develop`

Crie a branch da tarefa:

```bash
git switch develop
git pull origin develop
git switch -c feature/nome-da-funcionalidade
```

Depois de desenvolver e criar commits no padrão [Conventional Commits](../reference/architecture-standards/commit-convention-spec.md), publique a branch e abra o PR:

```bash
git push -u origin feature/nome-da-funcionalidade
```

O PR executa, conforme os caminhos alterados:

- Ruff format/lint, mypy, checks Django, migrations e Pytest no backend;
- lint, type-check, Vitest e `pnpm build` no frontend;
- `astro check` e build da landing;
- sincronização OpenAPI/Orval;
- build da imagem Docker de produção, sem push, seguido de smoke test do container;
- E2E em duas shards Playwright, somente Chromium;
- revisão por IA a cada novo SHA;
- para mudanças Terraform, apenas `fmt`, `init -backend=false` e `validate`.

O PR não autentica no GCP, não acessa o state remoto, não comenta um plano Terraform e não faz deploy. Corrija todos os checks antes do merge.

---

## 3. Faça o Merge em `develop`

O push resultante executa a CI novamente. Depois do sucesso de todos os gates, ela chama o workflow reutilizável de CD:

1. Alterações no backend publicam a imagem `wedding-api` no Artifact Registry, carregam os secrets da versão pinada, executam migrations e atualizam `wedding-backend-staging` no Cloud Run.
2. Alterações no frontend ou landing fazem deploy de preview na Vercel.
3. O Environment `Preview` seleciona as configurações do staging fixo; ele não representa um preview efêmero de PR.

Separadamente, `staging-pipeline.yml` autentica via WIF e planeja os dois roots relevantes:

```bash
terraform -chdir=terraform/shared plan
terraform -chdir=terraform/staging plan
```

Cada plano usa seu próprio prefixo GCS. O workflow de staging nunca executa `apply`.

Valide a aplicação no ambiente Preview antes de promover a Sprint.

---

## 4. Promova a Sprint para Produção

Abra um PR de `develop` para `main`. Ele repete os mesmos gates estáticos, builds e E2E do fluxo anterior. Mudanças em Terraform continuam recebendo somente validação local, sem comentário de plano e sem OIDC.

Após aprovação e merge em `main`:

1. a CI aprovada chama o CD no Environment `Production`;
2. os componentes alterados são implantados; o backend atualiza `wedding-backend` no Cloud Run com a imagem `wedding-api`, e frontend/landing seguem para a Vercel;
3. quando `terraform/**` ou o workflow Terraform mudou, `terraform-ci.yml` planeja `shared` e `production`; o apply permanece bloqueado até os imports convergirem e o opt-in ser habilitado manualmente.

As operações Terraform remotas são serializadas pelo grupo `terraform-remote-state`; os states permanecem separados por prefixo.

---

## 5. Faça um Hotfix

Crie o hotfix a partir de `main`:

```bash
git switch main
git pull origin main
git switch -c hotfix/corrige-login-google
```

Abra o PR para `main`. O deploy só acontece após aprovação, merge e sucesso da CI. Em seguida, sincronize `develop`:

```bash
git switch develop
git pull origin develop
git merge main
git push origin develop
```

---

## 6. Execute um Deploy Manual

Use `workflow_dispatch` de `cd-deploy.yml` apenas para recuperação operacional. Selecione `main` ou `develop`; outras branches não executam jobs de deploy. A execução manual implanta backend, frontend e landing, mantendo os Environments e secrets pinados da branch escolhida.
