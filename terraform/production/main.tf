locals {
  gcp_project_id = "gen-lang-client-0194045282"
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
  initial_image         = "us-central1-docker.pkg.dev/gen-lang-client-0194045282/cloud-run-source-deploy/wedding-backend@sha256:bf3700344958f8ba991c73342c3f15f912919be7e483e13f275cc6f167e341d1"
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
