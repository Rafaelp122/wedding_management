locals {
  gcp_project_id = data.terraform_remote_state.shared.outputs.gcp_project_id
  gcp_region     = "us-central1"
  environment    = "production"

  service_name    = "wedding-backend"
  database_secret = "neon-database" # pragma: allowlist secret
  django_secret   = "django-secret" # pragma: allowlist secret
  r2_bucket_name  = "wedding-management-prod"

  deployer_email = "github-actions-deployer@${local.gcp_project_id}.iam.gserviceaccount.com"
}

module "backend_service" {
  source = "../modules/gcp/cloud-run-service"

  environment           = local.environment
  service_name          = local.service_name
  gcp_region            = local.gcp_region
  database_secret_id    = local.database_secret
  django_secret_id      = local.django_secret
  r2_bucket_name        = local.r2_bucket_name
  cloudflare_account_id = var.cloudflare_account_id
  deployer_email        = local.deployer_email
  runtime_email         = data.terraform_remote_state.shared.outputs.runtime_sa_email
  web_app_project_id    = data.terraform_remote_state.shared.outputs.web_app_project_id
  vercel_target         = ["production"]
  vercel_git_branch     = "main"
  initial_image         = "${data.terraform_remote_state.shared.outputs.artifact_registry_repo_url}/wedding-api:6cc79ee97e64aeb2576ff8e2c114fbeebb660a1d"
  max_concurrency       = 15
}

moved {
  from = google_cloud_run_v2_service.wedding_api
  to   = module.backend_service.google_cloud_run_v2_service.wedding_api
}

moved {
  from = google_cloud_run_v2_service_iam_member.public_access
  to   = module.backend_service.google_cloud_run_v2_service_iam_member.public_access
}

moved {
  from = google_secret_manager_secret.database
  to   = module.backend_service.google_secret_manager_secret.database
}

moved {
  from = google_secret_manager_secret.django
  to   = module.backend_service.google_secret_manager_secret.django
}

moved {
  from = google_secret_manager_secret_iam_member.database_access
  to   = module.backend_service.google_secret_manager_secret_iam_member.database_access
}

moved {
  from = google_secret_manager_secret_iam_member.django_access
  to   = module.backend_service.google_secret_manager_secret_iam_member.django_access
}

moved {
  from = cloudflare_r2_bucket.contracts
  to   = module.backend_service.cloudflare_r2_bucket.contracts
}

moved {
  from = vercel_project_environment_variable.web_app_api_url
  to   = module.backend_service.vercel_project_environment_variable.web_app_api_url
}

# Cloud Scheduler Job para o lote diário de tarefas agendadas (Daily Batch Cron)
resource "google_cloud_scheduler_job" "daily_batch_cron" {
  name        = "wedding-daily-batch-cron-${local.environment}"
  description = "Dispara a execução em lote das tarefas diárias (ADR-005 e ADR-017)"
  schedule    = "0 2 * * *" # Diariamente às 02:00 AM (America/Sao_Paulo)
  time_zone   = "America/Sao_Paulo"
  region      = local.gcp_region

  http_target {
    http_method = "POST"
    uri         = "${module.backend_service.service_uri}/api/v1/internal/cron/daily-batch/"

    oidc_token {
      service_account_email = data.terraform_remote_state.shared.outputs.runtime_sa_email
      audience              = module.backend_service.service_uri
    }
  }

}
