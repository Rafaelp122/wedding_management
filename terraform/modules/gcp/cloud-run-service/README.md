# GCP Cloud Run Service Module

Este módulo reutilizável gerencia a implantação de serviços backend no Google Cloud Run v2, juntamente com suas dependências essenciais de infraestrutura.

## Recursos Gerenciados

- **Google Cloud Run v2**: Serviço Serverless containerizado com portas, limites de memória/CPU e auto-scaling.
- **IAM Invoker**: Permissão pública (`roles/run.invoker` para `allUsers`).
- **Secret Manager**: Containers para segredos do banco de dados e chave do Django (`prevent_destroy = true`).
- **IAM Secret Accessor**: Permissão `roles/secretmanager.secretAccessor` para a Service Account de deploy e runtime.
- **Cloudflare R2 Bucket**: Storage para contratos e arquivos do ambiente.
- **Vercel Environment Variable**: Registro automático da URL pública `VITE_API_URL` no projeto frontend Vercel.

## Exemplo de Uso

```hcl
module "backend_service" {
  source = "../modules/gcp/cloud-run-service"

  environment           = "staging"
  service_name          = "wedding-backend-staging"
  gcp_region            = "us-central1"
  database_secret_id    = "neon-database-staging"
  django_secret_id      = "django-secret-staging"
  r2_bucket_name        = "wedding-management-staging"
  cloudflare_account_id = var.cloudflare_account_id
  deployer_email        = "github-actions-deployer@project.iam.gserviceaccount.com"
  runtime_email         = "project-compute@developer.gserviceaccount.com"
  web_app_project_id    = "prj_vercel_id"
  vercel_target         = ["preview"]
  vercel_git_branch     = "develop"
  initial_image         = "us-central1-docker.pkg.dev/project/repo/wedding-api:latest"
  max_concurrency       = 80
}
```

## Entradas (Inputs)

| Nome | Descrição | Tipo | Padrão | Obrigatório |
|---|---|---|---|:---:|
| `environment` | Nome do ambiente (`staging` ou `production`) | `string` | N/A | Sim |
| `service_name` | Nome do serviço Cloud Run | `string` | N/A | Sim |
| `gcp_region` | Região GCP | `string` | `"us-central1"` | Não |
| `database_secret_id` | ID do segredo do banco no Secret Manager | `string` | N/A | Sim |
| `django_secret_id` | ID do segredo do Django no Secret Manager | `string` | N/A | Sim |
| `r2_bucket_name` | Nome do bucket R2 no Cloudflare | `string` | N/A | Sim |
| `cloudflare_account_id` | Account ID do Cloudflare | `string` | N/A | Sim |
| `deployer_email` | Service Account do CI/CD | `string` | N/A | Sim |
| `runtime_email` | Service Account de execução do Cloud Run | `string` | N/A | Sim |
| `web_app_project_id` | ID do projeto frontend na Vercel | `string` | N/A | Sim |
| `vercel_target` | Targets na Vercel (`preview` ou `production`) | `list(string)` | N/A | Sim |
| `vercel_git_branch` | Branch associada na Vercel | `string` | `null` | Não |
| `initial_image` | Imagem OCI inicial de referência | `string` | N/A | Sim |
| `max_concurrency` | Concorrência máxima por instância | `number` | `80` | Não |

## Saídas (Outputs)

| Nome | Descrição |
|---|---|
| `service_uri` | URI pública atribuída ao Cloud Run |
| `service_name` | Nome do serviço Cloud Run |
| `database_secret_id` | ID do segredo do banco de dados |
| `django_secret_id` | ID do segredo do Django |
| `r2_bucket_name` | Nome do bucket R2 gerenciado |
