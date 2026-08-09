# Especificação Técnica: Testes de Módulos Terraform (`tftest`)

> **Módulo:** [testing](index.md) | [ci-cd-pipeline-flow](../../4-explanation/architecture/ci-cd-pipeline-flow.md)
> **Camada:** Infraestrutura IaC (`Terraform` + `unit_test.tftest.hcl`)

---

## 1. Visão Geral

Os testes de infraestrutura no **Wedding Management System** garantem que os módulos HCL reutilizáveis em `terraform/modules/` respeitem seus contratos de variáveis, lifecycles de segurança (`prevent_destroy`, `ignore_changes`) e políticas de acesso sem realizar chamadas reais à nuvem nos Pull Requests.

---

## 2. Estrutura dos Arquivos de Teste

Cada módulo sob `terraform/modules/<provider>/<service-name>/` DEVE conter um arquivo de teste declarativo nativo do Terraform (`>= 1.7.0`):

```text
terraform/modules/gcp/cloud-run-service/
├── main.tf
├── variables.tf
├── outputs.tf
├── versions.tf
└── tests/
    └── unit_test.tftest.hcl   👈 Suíte de testes unitários do módulo
```

---

## 3. Diretrizes de Execução (`command = plan` & `mock_provider`)

1. **Execução em Modo `plan`**:
   Os testes de módulo em PRs **NUNCA** aplicam alterações (`apply`) nem acessam contas reais de provedores de nuvem. Toda suíte usa `command = plan`.
2. **Provedores Mockados (`mock_provider`)**:
   Utilize `mock_provider` nativo para isolar chamadas de API dos provedores (`google`, `cloudflare`, `vercel`).
3. **Casos Obrigatórios de Teste**:
   - **Happy Path**: Valida se a compilação do plano gera os recursos esperados com parâmetros padrão.
   - **Validação de Variáveis**: Testa parâmetros customizados e garante que valores inválidos sejam rejeitados pelas cláusulas `validation {}` em `variables.tf` (usando `expect_failures`).

```hcl
# Exemplo: unit_test.tftest.hcl
mock_provider "google" {}
mock_provider "cloudflare" {}
mock_provider "vercel" {}

run "verify_cloud_run_defaults" {
  command = plan

  variables {
    project_id   = "test-project-123"
    environment  = "staging"
    service_name = "wedding-backend"
  }

  assert {
    condition     = google_cloud_run_v2_service.wedding_api.ingress == "INGRESS_TRAFFIC_ALL"
    error_message = "Ingress do Cloud Run deve ser INGRESS_TRAFFIC_ALL"
  }
}
```

---

## 4. Integração na CI/CD Pipeline

O workflow [terraform-ci.yml](../../../.github/workflows/terraform-ci.yml) executa automaticamente os testes de Terraform em Pull Requests:

```bash
# Comando executado na CI
terraform test
```

### Gate de Qualidade
A pipeline de PR falha se qualquer asserção (`assert`) ou validação de variável falhar nos testes `.tftest.hcl`.
