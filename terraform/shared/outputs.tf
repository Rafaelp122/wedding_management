output "artifact_registry_repo_url" {
  description = "URL do repositório OCI compartilhado"
  value       = "${local.gcp_region}-docker.pkg.dev/${local.gcp_project_id}/${google_artifact_registry_repository.backend_repo.repository_id}"
}

output "web_app_project_id" {
  description = "ID do projeto Vercel do frontend"
  value       = vercel_project.web_app.id
}

output "landing_project_id" {
  description = "ID do projeto Vercel da landing"
  value       = vercel_project.landing.id
}

output "wif_provider_name" {
  description = "Nome completo do provider WIF usado pelo GitHub Actions"
  value       = google_iam_workload_identity_pool_provider.github_provider.name
}

output "github_deployer_sa_email" {
  description = "Service Account representada pelo GitHub Actions"
  value       = google_service_account.github_deployer.email
}
