locals {
  gcp_project_id = data.terraform_remote_state.shared.outputs.gcp_project_id
  gcp_region     = "us-central1"
  environment    = "staging"

  service_name               = "wedding-backend-staging"
  database_secret            = "neon-database-staging"           # pragma: allowlist secret
  django_secret              = "django-secret-staging"           # pragma: allowlist secret
  email_smtp_user_secret     = "email-smtp-user-staging"         # pragma: allowlist secret
  email_smtp_password_secret = "email-smtp-password-staging"     # pragma: allowlist secret
  r2_bucket_name             = "wedding-management-staging"

  deployer_email = "github-actions-deployer@${local.gcp_project_id}.iam.gserviceaccount.com"
}

module "backend_service" {
  source = "../modules/gcp/cloud-run-service"

  environment                   = local.environment
  service_name                  = local.service_name
  gcp_region                    = local.gcp_region
  database_secret_id            = local.database_secret
  django_secret_id              = local.django_secret
  email_smtp_user_secret_id     = local.email_smtp_user_secret
  email_smtp_password_secret_id = local.email_smtp_password_secret
  r2_bucket_name                = local.r2_bucket_name
  cloudflare_account_id         = var.cloudflare_account_id
  deployer_email                = local.deployer_email
  runtime_email                 = data.terraform_remote_state.shared.outputs.runtime_sa_email
  web_app_project_id            = data.terraform_remote_state.shared.outputs.web_app_project_id
  vercel_target                 = ["preview"]
  vercel_git_branch             = "develop"
  initial_image                 = "${data.terraform_remote_state.shared.outputs.artifact_registry_repo_url}/wedding-api:6cc79ee97e64aeb2576ff8e2c114fbeebb660a1d"
  max_concurrency               = 80
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
