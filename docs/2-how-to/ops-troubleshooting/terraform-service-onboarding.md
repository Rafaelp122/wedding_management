# Como Adicionar e Manter Serviços na Infraestrutura Terraform

> **Relacionados:** [ADR-025](../../4-explanation/adr/025-terraform-iac-architecture.md) | [ADR-027](../../4-explanation/adr/027-terraform-state-topology.md) | [terraform-modules-spec](../../3-reference/architecture-standards/terraform-modules-spec.md) | [ci-cd-pipeline-flow](../../4-explanation/architecture/ci-cd-pipeline-flow.md)

Este guia orienta os engenheiros sobre como manter a infraestrutura atual e como adicionar novos serviços (como GCP Memorystore/Redis, Cloud Tasks/Celery, Cloud Run Jobs, Cloud Scheduler, recursos adicionais da Cloudflare e Vercel) seguindo os padrões de modularização do projeto.

---

## 🏛️ Organização da Arquitetura por Provedores

### Por que separamos por provedores sob `terraform/modules/`?
Inicialmente, recursos menores da Cloudflare (R2 Bucket) e Vercel (Variáveis de Ambiente) foram encapsulados junto ao módulo do Cloud Run. Conforme o ecossistema cresce, a boa prática (descrita em `terraform-module-library`) é organizar os módulos por provedor:

```text
terraform/modules/
├── gcp/
│   ├── cloud-run-service/    # Backend API e contêineres Cloud Run v2
│   ├── redis-cache/          # Future: GCP Memorystore para cache e Celery
│   ├── cloud-tasks-queue/    # Future: Fila de tarefas assíncronas / Celery
│   └── cloud-scheduler-job/  # Future: Tarefas agendadas e crons
├── cloudflare/
│   └── r2-bucket/            # Future: Módulo dedicado para storage de contratos
└── vercel/
    └── project-env-vars/     # Future: Módulo dedicado para gestão de ambientes Vercel
```

---

## 📋 Estrutura Padrão de um Módulo Reutilizável

Todo novo módulo deve conter exatamente 5 arquivos essenciais, seguindo o `terraform-style-guide` e `terraform-module-library`:

| Arquivo | Função e Convenção |
|---|---|
| `versions.tf` | Define a versão fixa do Terraform (`= 1.7.5`) e dos provedores necessários. |
| `variables.tf` | Declara entradas fortemente tipadas com `validation {}`. **NUNCA** inclua defaults hardcoded de IDs de projetos GCP ou credenciais reais. |
| `main.tf` | Recursos HCL do provedor, usando `prevent_destroy = true` para recursos persistentes (bancos, segredos, buckets) e `labels = { environment = var.environment }`. |
| `outputs.tf` | Exposição de atributos essenciais com descrições em PT-BR devidamente acentuadas. |
| `tests/unit_test.tftest.hcl` | Teste unitário declarativo nativo rodando em modo `command = plan` com `mock_provider`. |

---

## 🛠️ Passo a Passo: Como Criar e Adicionar um Novo Serviço

### Passo 1: Criar o Módulo em `terraform/modules/<provider>/<service-name>`
Defina as variáveis em `variables.tf`, os recursos em `main.tf` e os outputs em `outputs.tf`.

Exemplo de declaração com suporte a rótulos de ambiente:
```hcl
# terraform/modules/gcp/redis-cache/main.tf
resource "google_memorystore_instance" "cache" {
  name           = var.instance_name
  memory_size_gb = var.memory_size_gb

  labels = {
    environment = var.environment
  }

  lifecycle {
    prevent_destroy = true
  }
}
```

### Passo 2: Escrever Testes Unitários Nativos (`terraform-test`)
Crie a suíte de teste offline utilizando `mock_provider` nativo do Terraform 1.7.5 para validar portas, limites de recursos e regras de nomeação sem depender de acesso à nuvem real:

```hcl
# terraform/modules/gcp/redis-cache/tests/unit_test.tftest.hcl
mock_provider "google" {}

variables {
  environment    = "staging"
  instance_name  = "wedding-redis-staging"
  memory_size_gb = 1
}

run "validate_redis_configuration" {
  command = plan

  assert {
    condition     = google_memorystore_instance.cache.memory_size_gb == 1
    error_message = "A memória inicial do Redis deve ser de 1GB."
  }
}
```

Para rodar os testes localmente:
```bash
/tmp/terraform-1.7.5/terraform -chdir=terraform/modules/gcp/redis-cache test
```

### Passo 3: Instanciar nos Chamadores (`staging` e `production`)
Adicione a chamada do módulo nos arquivos chamadores dos ambientes `terraform/staging/main.tf` e `terraform/production/main.tf`:

```hcl
module "redis_cache" {
  source = "../modules/gcp/redis-cache"

  environment    = local.environment
  instance_name  = "wedding-redis-${local.environment}"
  memory_size_gb = local.environment == "production" ? 4 : 1
}
```

### Passo 4: Preservar Recursos Existentes com Blocos `moved {}` (Skill `refactor-module`)
Se o recurso já existir na nuvem real antes da declaração no Terraform, adicione o bloco `moved {}` no arquivo do ambiente para evitar que o Terraform tente destruí-lo e recriá-lo:

```hcl
moved {
  from = google_memorystore_instance.legacy_cache
  to   = module.redis_cache.google_memorystore_instance.cache
}
```

### Passo 5: Validação Offline e Auditoria de Documentação
Antes de abrir o Pull Request, execute a suíte de validação:

```bash
/tmp/terraform-1.7.5/terraform fmt -check -recursive terraform
./.codex-terraform-gcloud.sh -chdir=terraform/staging validate
./.codex-terraform-gcloud.sh -chdir=terraform/production validate
make check-docs
```

---

## 🔮 Exemplos Práticos para Futuros Serviços

- **Tarefas Agendadas (Cloud Scheduler)**: Criar `terraform/modules/gcp/cloud-scheduler-job/` para agendar crons como a marcação automática de parcelas vencidas (`/api/v1/finances/installments/mark-overdue/`).
- **Filas Assíncronas (Cloud Tasks)**: Criar `terraform/modules/gcp/cloud-tasks-queue/` para processar envios de e-mail e uploads pesados sem bloquear o worker HTTP.
- **Cache de Sessão e Rate Limit (GCP Memorystore / Redis)**: Criar `terraform/modules/gcp/redis-cache/` para suporte a cache distribuído e controle de taxa de requisições.
