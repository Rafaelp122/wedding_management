# Especificação Técnica: Módulo `gcp/cloud-run-service`

> **Módulo:** [terraform](index.md) | [ADR-025](../../architecture/adr/025-terraform-iac-architecture.md)
> **Caminho:** `terraform/modules/gcp/cloud-run-service/`

---

## 1. Visão Geral

O módulo **`gcp/cloud-run-service`** é responsável pelo provisionamento declarativo do serviço Cloud Run v2, containers de segredos no Secret Manager, buckets R2 associados no Cloudflare e injeção automática de variáveis de ambiente na Vercel.

---

## 2. Recursos Gerenciados

- `google_cloud_run_v2_service.wedding_api`: Serviço Cloud Run v2 (Porta 8080, ingress `INGRESS_TRAFFIC_ALL`).
- `google_cloud_run_v2_service_iam_member.public_access`: Binding público `roles/run.invoker` para `allUsers`.
- `google_secret_manager_secret.database`: Container do segredo de banco de dados (`prevent_destroy = true`).
- `google_secret_manager_secret.django`: Container do segredo Django (`prevent_destroy = true`).
- `google_secret_manager_secret.email_smtp_password`: Container do segredo da senha/API key SMTP (`prevent_destroy = true`).
- `google_secret_manager_secret_iam_member.database_access`: Permissão `roles/secretmanager.secretAccessor` para deployer e runtime SA.
- `google_secret_manager_secret_iam_member.django_access`: Permissão `roles/secretmanager.secretAccessor` para deployer e runtime SA.
- `google_secret_manager_secret_iam_member.email_smtp_password_access`: Permissão `roles/secretmanager.secretAccessor` para deployer e runtime SA.
- `cloudflare_r2_bucket.contracts`: Bucket R2 no Cloudflare para contratos (`prevent_destroy = true`).
- `vercel_project_environment_variable.web_app_api_url`: Registro automático da variável `VITE_API_URL` na Vercel.

---

## 3. Lifecycles e Guard-Rails

1. **`prevent_destroy = true`**: Protege os containers de segredos, serviço Cloud Run e bucket R2 contra destruição acidental.
2. **`ignore_changes`**:
   - No Cloud Run: Ignora `template[0].containers[0].image`, `env`, `resources` e `startup_probe`, permitindo que o CD (GitHub Actions) atualize a imagem e variáveis de runtime sem que o Terraform as reverte.

---

## 4. Suíte de Testes Declarativos (`unit_test.tftest.hcl`)

Os testes do módulo rodam sob `terraform test` usando `mock_provider` nativo (consulte [terraform-testing-spec](../testing/terraform-testing-spec.md)).
