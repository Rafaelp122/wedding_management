# 📐 Especificação Técnica de Módulos Terraform — Wedding Management System

> **Versão:** 1.0 | **Última atualização:** 7 de agosto de 2026
> **Relacionados:** [ADR-025](../../4-explanation/adr/025-terraform-iac-architecture.md) | [ADR-027](../../4-explanation/adr/027-terraform-state-topology.md) | [ci-cd-pipeline-flow](../../4-explanation/architecture/ci-cd-pipeline-flow.md) | [terraform-service-onboarding](../../2-how-to/ops-troubleshooting/terraform-service-onboarding.md)

---

## 1. Visão Geral

Esta especificação define os padrões de desenvolvimento, contrato e estrutura para módulos reutilizáveis do Terraform no projeto. A documentação segue o princípio de **Single Source of Truth (SSOT)**: as especificações oficiais residem sob `docs/` e o código sob `terraform/modules/` consome esta referência.

---

## 2. Convenção de Diretórios por Provedor

Os módulos reutilizáveis são organizados estritamente pelo provedor sob `terraform/modules/`:

```text
terraform/modules/
├── gcp/
│   ├── cloud-run-service/    # Módulo GCP Cloud Run v2, Secrets e IAM
│   ├── redis-cache/          # Future: GCP Memorystore para cache/Celery
│   ├── cloud-tasks-queue/    # Future: Filas assíncronas do Cloud Tasks
│   └── cloud-scheduler-job/  # Future: Crons agendadas do Cloud Scheduler
├── cloudflare/
│   └── r2-bucket/            # Future: Storage R2 de contratos
└── vercel/
    └── project-env-vars/     # Future: Gestão de variáveis da Vercel
```

---

## 3. Estrutura Padrão do Módulo (Contrato de 5 Arquivos)

Cada módulo sob `terraform/modules/<provider>/<service-name>/` deve conter os seguintes arquivos:

| Arquivo | Responsabilidade |
|---|---|
| `versions.tf` | Versão travada do Terraform (`= 1.7.5`) e providers necessários. |
| `variables.tf` | Inputs tipados com `validation {}`. **NUNCA** inclua defaults hardcoded de IDs de projetos GCP ou credenciais. |
| `main.tf` | Recursos HCL do provedor. Recursos de dados devem usar `prevent_destroy = true` e `labels = { environment = var.environment }`. |
| `outputs.tf` | Atributos expostos com `description` em PT-BR acentuada. |
| `tests/unit_test.tftest.hcl` | Suíte de testes declarativos nativos rodando em modo `command = plan` com `mock_provider`. |

---

## 4. Especificação Técnica: `gcp/cloud-run-service`

### Recursos Gerenciados

- `google_cloud_run_v2_service.wedding_api`: Serviço Cloud Run v2 (Porta 8080, ingress `INGRESS_TRAFFIC_ALL`).
- `google_cloud_run_v2_service_iam_member.public_access`: Binding público `roles/run.invoker` para `allUsers`.
- `google_secret_manager_secret.database`: Container do segredo de banco de dados (`prevent_destroy = true`).
- `google_secret_manager_secret.django`: Container do segredo Django (`prevent_destroy = true`).
- `google_secret_manager_secret_iam_member.database_access`: Permissão `roles/secretmanager.secretAccessor` para o deployer e a runtime SA.
- `google_secret_manager_secret_iam_member.django_access`: Permissão `roles/secretmanager.secretAccessor` para o deployer e a runtime SA.
- `cloudflare_r2_bucket.contracts`: Bucket R2 no Cloudflare para contratos (`prevent_destroy = true`).
- `vercel_project_environment_variable.web_app_api_url`: Registro automático da variável `VITE_API_URL` na Vercel.

### Raciocínio de Lifecycles (Guard-Rails)

1. **`prevent_destroy = true`**: Protege os containers de segredos, Cloud Run e bucket R2 contra destruição acidental.
2. **`ignore_changes`**:
   - No Cloud Run: Ignora `template[0].containers[0].image`, `env`, `resources` e `startup_probe`, permitindo que o CD (GitHub Actions / Cloud Build) atualize a imagem e variáveis de runtime sem que o Terraform as reverte.

---

## 5. Diretrizes de Testes Unitários Nativos (`terraform-test`)

- Os testes de módulos sob `modules/` rodam em modo `command = plan` e **NUNCA** acessam a nuvem real em Pull Requests.
- Devem utilizar os `mock_provider` nativos do Terraform 1.7.5 (`google`, `cloudflare`, `vercel`).
- Devem cobrir cenários felizes (happy path), cenários com parâmetros customizados e **cenários negativos de validação de variáveis** (`expect_failures`).
