# terraform/outputs.tf
# Valores de saída exportados pelo Terraform após o provisionamento dos recursos.

output "cloud_run_url" {
  description = "URL pública de invocação do backend Cloud Run"
  value       = google_cloud_run_v2_service.wedding_api.uri
}

output "artifact_registry_repo_url" {
  description = "URL do repositório no Google Artifact Registry para push de imagens Docker"
  value       = "${var.gcp_region}-docker.pkg.dev/${var.gcp_project_id}/${google_artifact_registry_repository.backend_repo.repository_id}"
}

output "wif_provider_name" {
  description = "Nome completo do recurso do Provedor Workload Identity Federation (para secret GCP_WIF_PROVIDER)"
  value       = google_iam_workload_identity_pool_provider.github_provider.name
}

output "github_deployer_sa_email" {
  description = "E-mail da Service Account usada pelo GitHub Actions (para secret GCP_WIF_SERVICE_ACCOUNT)"
  value       = google_service_account.github_deployer.email
}

output "r2_bucket_name" {
  description = "Nome do bucket R2 no Cloudflare para armazenamento de contratos"
  value       = cloudflare_r2_bucket.contracts_bucket.name
}
