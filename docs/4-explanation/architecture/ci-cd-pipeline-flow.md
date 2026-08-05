# 🔁 Especificação da Arquitetura Modular de CI/CD — Wedding Management System

> **Versão:** 3.1 | **Última atualização:** 3 de agosto de 2026
> **Relacionados:** [ADR-025](../adr/025-terraform-iac-architecture.md) | [ADR-026](../adr/026-gitops-branching-and-deployment-strategy.md) | [gitops-sprint-workflow](../../1-tutorials/gitops-sprint-workflow.md)

---

## 1. Visão Geral

As pipelines separam validação, deploy da aplicação e gestão da infraestrutura:

1. **CI** valida código, contratos, testes, builds do frontend/landing e a imagem do backend com smoke test, sem publicar artefatos.
2. **CD** é um workflow reutilizável chamado pela CI somente após um `push` aprovado em `main` ou `develop`. Também aceita execução manual, restrita a essas branches.
3. **Terraform** valida configuração de PR sem credenciais; operações com estado remoto e WIF ocorrem apenas em branches protegidas.
4. **Revisão por IA** roda em cada SHA enviado ao PR, sem usar labels como estado.

```mermaid
flowchart TD
    PR[PR para main ou develop] --> CI[CI: lint, tipos, testes, contratos e build Docker]
    CI --> E2E[E2E reutilizável: Playwright Chromium]
    PR --> AI[Revisão por IA em cada SHA]
    PR --> TFV[Terraform: fmt, init sem backend e validate]

    PUSH[Push aprovado em main ou develop] --> CI
    E2E -->|sucesso em push| CD[CD reutilizável]
    CD --> MIGRATE[Migrations Django]
    MIGRATE --> RUN[Cloud Run]
    CD --> VERCEL[Vercel]

    MAIN[Push em main com mudança Terraform] --> APPLY[Apply de produção bloqueado até imports]
    DEVELOP[Push em develop] --> STAGING[Terraform plan-only no state compartilhado]
    MANUAL[workflow_dispatch em main ou develop] --> CD
```

---

## 2. Gatilhos e Escopos

| Workflow | Gatilho | Escopo de caminhos | Responsabilidade |
|:---|:---|:---|:---|
| **[ci-pr-validation.yml](../../../.github/workflows/ci-pr-validation.yml)** | `pull_request` e `push` em `main`/`develop` | Filtros internos para `backend/**`, `frontend/**`, `landing/**`, manifests compartilhados e arquivos da própria CI | Ruff format/lint, mypy, Pytest, migrations check, Vitest com cobertura, `pnpm build` no PR, isolamento de mocks, Astro, contratos OpenAPI/Orval e build Docker com smoke test sem push. Em `push`, chama o CD somente após sucesso dos gates. |
| **[docs-ci.yml](../../../.github/workflows/docs-ci.yml)** | `pull_request` e `push` em `main`/`develop` | `docs/**`, Markdown, workflow de docs, `Makefile` e validador de links | Executa `make check-docs`. |
| **[e2e-tests.yml](../../../.github/workflows/e2e-tests.yml)** | `workflow_call` pela CI | Alterações em backend, frontend ou no próprio workflow, detectadas pela CI | Executa Playwright em Chromium, dividido em duas shards, sobre Uvicorn ASGI; seu sucesso é obrigatório antes do CD automático. |
| **[ai-code-review.yml](../../../.github/workflows/ai-code-review.yml)** | PR para `main`/`develop`: `opened`, `synchronize`, `reopened` | Todo o diff do PR | Executa OpenCode em cada novo SHA; não cria nem consulta a label `ai-reviewed`. |
| **[cd-deploy.yml](../../../.github/workflows/cd-deploy.yml)** | `workflow_call` após CI de `push`; `workflow_dispatch` guardado | Filtros internos para backend, frontend e landing; execução manual implanta todos os componentes | Publica backend no Artifact Registry, migra o banco antes do Cloud Run e implanta frontend/landing na Vercel. Não roda em PR. |
| **[terraform-ci.yml](../../../.github/workflows/terraform-ci.yml)** | PR e `push` em `main`/`develop` | `terraform/**` e workflows Terraform/staging | Sempre executa `fmt`, `init -backend=false` e `validate`, sem OIDC. O job de `apply` em `main` só roda quando a repository variable `TERRAFORM_PRODUCTION_APPLY_ENABLED` é exatamente `true`. |
| **[staging-pipeline.yml](../../../.github/workflows/staging-pipeline.yml)** | `push` em `develop`; `workflow_dispatch` | Todos os pushes em `develop` | Autentica com WIF e executa somente um plano contra o state atualmente compartilhado. Não roda em PR e nunca deve aplicar esse plano. |

O `workflow_dispatch` do CD não executa deploy fora de `main` ou `develop`. Pull requests nunca recebem a identidade de deploy.

---

## 3. Fluxo de Validação e Deploy

### Pull request

- A CI executa apenas os jobs relacionados aos caminhos alterados; mudanças nos workflows e composite actions acionam seus consumidores.
- O frontend executa `pnpm build`; a imagem de produção do backend é compilada, carregada localmente e precisa responder ao health check do smoke test. Não há login no Artifact Registry nem publicação da imagem.
- O E2E cobre somente Chromium e integra o gate da CI.
- Cada evento `synchronize` inicia uma nova revisão por IA para o SHA atual.
- Mudanças Terraform usam `terraform init -backend=false`; portanto, não acessam o state remoto nem solicitam token OIDC.

### Push em branch protegida

- A CI executa os gates e chama `cd-deploy.yml` apenas após todos os jobs obrigatórios terem sucesso.
- `develop` seleciona o GitHub Environment `Preview`; `main`, `Production`.
- O backend publica `us-central1-docker.pkg.dev/<project_id>/wedding-management-repo/wedding-api:<sha>` e usa os serviços Cloud Run `wedding-backend-staging` em Preview ou `wedding-backend` em Production.
- Após o WIF, `google-github-actions/get-secretmanager-secrets@v3` lê as versões pinadas de `DATABASE_URL` e `SECRET_KEY`; esses outputs alimentam somente a migration executada antes do deploy.
- O Cloud Run recebe referências `secret-id:versão` nos campos de secret da action oficial de deploy e resolve os valores em runtime diretamente no Secret Manager.
- O CD injeta `ALLOWED_HOSTS` e `CORS_ALLOWED_ORIGINS` com valores estáticos específicos da branch, além de `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET` e `R2_ENDPOINT_URL` vindos dos GitHub Secrets existentes.
- `google-github-actions/deploy-cloudrun` cria o serviço quando ausente ou atualiza o existente; `flags: --allow-unauthenticated` mantém a API pública.
- O frontend e a landing usam preview em `develop` e produção em `main`.

Falha em qualquer gate impede a chamada automática do CD. A execução manual existe para recuperação operacional, mas mantém a restrição de branch e os mesmos ambientes.

---

## 4. Terraform e Concorrência de State

Pull requests fazem apenas validação local e não disputam o lock do backend remoto. Os workflows remotos estão serializados, mas ainda usam o mesmo bucket e prefixo de state:

- `push` em `main`: `terraform-ci.yml` só gera e aplica o plano de `environments/production.tfvars` quando `TERRAFORM_PRODUCTION_APPLY_ENABLED == 'true'`; vazia, ausente ou com outro valor, a variável bloqueia o job.
- `push` em `develop`: `staging-pipeline.yml` calcula um plano com `environments/staging.tfvars` contra o state compartilhado, somente para inspeção.

As operações remotas compartilham o grupo de concorrência `terraform-remote-state`, evitando disputa simultânea pelo lock, mas isso não isola os ambientes.

> [!WARNING]
> O state GCS atual ainda não adotou os recursos que já existem no GCP, Vercel e demais providers. Mantenha `TERRAFORM_PRODUCTION_APPLY_ENABLED` ausente ou diferente de `true` até inventariar a infraestrutura real, importar cada recurso para o state de produção e revisar um plano sem criações, substituições ou remoções inesperadas. Aplicar antes disso pode tentar recriar ou destruir recursos ativos.
>
> Staging e produção também compartilham hoje o mesmo backend/prefixo. Separar os states e os targets por ambiente é uma dívida independente dos imports. Até essa separação, o plano de staging não comprova drift isolado e jamais deve ser aplicado.

---

## 5. Autenticação, Secret Manager e Configuração

O GitHub autentica no GCP por Workload Identity Federation. O provider aceita somente execuções de `main`/`develop` originadas dos workflows CI, CD, Terraform ou staging autorizados; PRs não podem representar a Service Account de deploy.

Os valores de `DATABASE_URL` e `SECRET_KEY` existem somente no GCP Secret Manager. Os GitHub Environments `Preview` e `Production` guardam estas variáveis não sensíveis:

| Variável de Environment | Conteúdo |
|:---|:---|
| `GCP_DATABASE_SECRET_ID` | ID do secret que contém `DATABASE_URL`. |
| `GCP_DATABASE_SECRET_VERSION` | Versão numérica habilitada; nunca usar `latest`. |
| `GCP_DJANGO_SECRET_ID` | ID do secret que contém `SECRET_KEY`. |
| `GCP_DJANGO_SECRET_VERSION` | Versão numérica habilitada; nunca usar `latest`. |

Os outputs internos `database_url` e `django_secret_key` da action do Secret Manager não são exportados globalmente. O primeiro é usado com o segundo na migration; o Cloud Run recebe somente referências aos secrets pinados.

As demais credenciais continuam como GitHub Secrets:

| Nome | Tipo | Uso |
|:---|:---|:---|
| `GCP_WIF_PROVIDER` | Secret | Identificador do provider WIF usado por CD e Terraform autenticado. |
| `GCP_WIF_SERVICE_ACCOUNT` | Secret | Service Account de deploy com permissões mínimas no Artifact Registry, Cloud Run e Terraform. |
| `VERCEL_TOKEN` | Secret | Autenticação dos deploys Vercel e do provider Terraform. |
| `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID_FRONTEND`, `VERCEL_PROJECT_ID_LANDING` | Secret | Destinos Vercel da aplicação e da landing. |
| `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET`, `R2_ENDPOINT_URL` | Secret | Configuração R2 injetada no runtime do backend. |
| `CLOUDFLARE_API_TOKEN` | Secret | Credencial do provider Cloudflare no Terraform. |
| `CODECOV_TOKEN` | Secret | Upload opcional de cobertura. |
| `DEEPSEEK_API_KEY` | Secret | Revisor de código OpenCode. |

`GCP_PROJECT_ID` não é cadastrado como secret. O CD usa `steps.auth.outputs.project_id`, fornecido pela ação de autenticação, para montar a URL do Artifact Registry. O Terraform recebe o projeto pelos arquivos `.tfvars` versionados.

`TERRAFORM_PRODUCTION_APPLY_ENABLED` é uma repository variable e não um secret. O padrão seguro é mantê-la vazia, removida ou como `false`, bloqueando o job de produção. Defina-a como `true` somente após concluir inventário, imports, separação segura do state de produção e revisão do plano; remova-a ou volte para `false` para bloquear novamente.

### Bootstrap manual de IAM e Secret Manager

O primeiro provisionamento não pode depender da identidade que ele próprio cria. Um operador autenticado no GCP deve executar inicialmente o Terraform com credenciais administrativas para criar o pool/provider WIF, a Service Account de deploy e seus bindings. Depois, cadastre `GCP_WIF_PROVIDER` e `GCP_WIF_SERVICE_ACCOUNT` no GitHub.

Antes do primeiro deploy em `develop`, crie manualmente o repositório esperado pelo CD:

```bash
export PROJECT_ID="seu-projeto-gcp"
gcloud artifacts repositories create wedding-management-repo \
  --repository-format=docker \
  --location=us-central1 \
  --project="$PROJECT_ID"
```

Como esse repositório também é declarado pelo Terraform, importe-o em `google_artifact_registry_repository.backend_repo` antes de liberar o `apply`; caso contrário, o plano tentará criar um recurso que já existe. O ID de import é `projects/<project_id>/locations/us-central1/repositories/wedding-management-repo`.

O primeiro deploy pode criar `wedding-backend-staging`; não é necessário criar o serviço Cloud Run antes. Porém, o Environment `Preview`, seus quatro `GCP_*_SECRET_*`, os secrets R2 e os secrets separados de banco/Django precisam existir, e a Service Account de deploy deve ter `roles/secretmanager.secretAccessor`, antes desse run.

O conteúdo dos secrets não é gerenciado pelo Terraform nem versionado no repositório. Os IDs não são fixados pelo workflow: secrets existentes podem ser reutilizados, desde que o Environment aponte para o ID e a versão corretos. No estado atual, Production pode reutilizar `neon-database` versão `1` e `django-secret` versão `1`.

Preview deve usar secrets próprios para nunca conectar o staging ao banco ou à chave de Production. Se ainda não existirem, crie-os com IDs distintos; os nomes abaixo são apenas uma sugestão:

```bash
gcloud services enable secretmanager.googleapis.com --project="$PROJECT_ID"

export PREVIEW_DATABASE_SECRET_ID="neon-database-staging"
export PREVIEW_DJANGO_SECRET_ID="django-secret-staging"

for SECRET_ID in "$PREVIEW_DATABASE_SECRET_ID" "$PREVIEW_DJANGO_SECRET_ID"
do
  gcloud secrets create "$SECRET_ID" --replication-policy=automatic --project="$PROJECT_ID"
done
```

Adicione somente os valores de Preview pela entrada padrão para não colocá-los no comando ou no repositório. Se os secrets já existirem, pule a criação e adicione uma nova versão apenas quando necessário:

```bash
gcloud secrets versions add "$PREVIEW_DATABASE_SECRET_ID" --data-file=- --project="$PROJECT_ID"
gcloud secrets versions add "$PREVIEW_DJANGO_SECRET_ID" --data-file=- --project="$PROJECT_ID"
```

A Service Account de deploy precisa ler os valores durante migrations; a identidade de runtime do Cloud Run precisa resolver as referências. Enquanto os serviços usam a Compute Engine default Service Account, conceda acesso no nível de cada secret:

```bash
export DEPLOYER_SA="github-actions-deployer@${PROJECT_ID}.iam.gserviceaccount.com"
export PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"
export RUNTIME_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

for SECRET_ID in \
  neon-database \
  django-secret \
  "$PREVIEW_DATABASE_SECRET_ID" \
  "$PREVIEW_DJANGO_SECRET_ID"
do
  gcloud secrets add-iam-policy-binding "$SECRET_ID" --project="$PROJECT_ID" \
    --member="serviceAccount:${DEPLOYER_SA}" --role=roles/secretmanager.secretAccessor
  gcloud secrets add-iam-policy-binding "$SECRET_ID" --project="$PROJECT_ID" \
    --member="serviceAccount:${RUNTIME_SA}" --role=roles/secretmanager.secretAccessor
done
```

Por fim, registre os IDs e as versões numéricas correspondentes como variables, não secrets, nos Environments:

```bash
gh variable set GCP_DATABASE_SECRET_ID --env Preview --body "$PREVIEW_DATABASE_SECRET_ID"
gh variable set GCP_DATABASE_SECRET_VERSION --env Preview --body 1
gh variable set GCP_DJANGO_SECRET_ID --env Preview --body "$PREVIEW_DJANGO_SECRET_ID"
gh variable set GCP_DJANGO_SECRET_VERSION --env Preview --body 1

gh variable set GCP_DATABASE_SECRET_ID --env Production --body neon-database
gh variable set GCP_DATABASE_SECRET_VERSION --env Production --body 1
gh variable set GCP_DJANGO_SECRET_ID --env Production --body django-secret
gh variable set GCP_DJANGO_SECRET_VERSION --env Production --body 1
```

Ao rotacionar um valor, crie uma nova versão no Secret Manager e atualize somente a variável `*_VERSION` após validá-la. A versão anterior permanece disponível para rollback.

### Bootstrap do target Preview na Vercel

Depois que o primeiro deploy criar `wedding-backend-staging`, obtenha a URL pública do serviço e configure `VITE_API_URL` no target Preview do projeto frontend:

```bash
gcloud run services describe wedding-backend-staging \
  --region=us-central1 \
  --project="$PROJECT_ID" \
  --format='value(status.url)'
```

Cadastre a URL retornada no painel da Vercel ou com `vercel env add VITE_API_URL preview`. Configure `PUBLIC_API_URL` no target Preview da landing somente se o projeto efetivamente consumir essa variável.

O Terraform atual vincula os targets `production` e `preview` à mesma URL de API. Não use esse recurso para sobrescrever o Preview enquanto os states e targets não estiverem separados; esse acoplamento é parte da dívida que bloqueia o `apply`.

---

## 6. Gates de Qualidade

| Gate | Critério de aceitação |
|:---|:---|
| Documentação | `make check-docs` sem links quebrados. |
| Contratos | Nenhum diff após exportar OpenAPI e gerar o cliente Orval. |
| Backend | Ruff, mypy, Django checks, migrations e Pytest aprovados. |
| Frontend | Lint, type-check, isolamento de mocks, Vitest com cobertura e `pnpm build` no PR aprovados. |
| Landing | `astro check` e build aprovados. |
| Container | Build da imagem de produção e health check do container aprovados sem push em PR. |
| E2E | Duas shards Playwright em Chromium aprovadas. |

---

## 7. ADRs Relacionados

- [ADR-025: Adoção de Terraform e GitOps Multi-Cloud](../adr/025-terraform-iac-architecture.md)
- [ADR-026: Estratégia de Branches, Homologação e Sprints](../adr/026-gitops-branching-and-deployment-strategy.md)
- [ADR-012: Orval Contract-Driven Frontend](../adr/012-orval-contract-driven-frontend.md)
- [ADR-018: Playwright E2E Testing](../adr/018-playwright-e2e-testing.md)
