mock_provider "google" {}
mock_provider "cloudflare" {}
mock_provider "vercel" {}

variables {
  environment                = "staging"
  service_name               = "wedding-backend-staging"
  database_secret_id         = "neon-database-staging"
  django_secret_id           = "django-secret-staging"
  r2_bucket_name             = "wedding-management-staging"
  cloudflare_account_id      = "81bf3d86c07ecf0f6181ea7e6aaf8dea"
  deployer_email             = "github-actions-deployer@gen-lang-client-0194045282.iam.gserviceaccount.com"
  runtime_email              = "597398840710-compute@developer.gserviceaccount.com"
  artifact_registry_repo_url = "us-central1-docker.pkg.dev/gen-lang-client-0194045282/wedding-management-repo"
  web_app_project_id         = "prj_Nozh5iaNEpJxkMMq50HqR6IR9AIj"
  vercel_target              = ["preview"]
  vercel_git_branch          = "develop"
  initial_image              = "us-central1-docker.pkg.dev/gen-lang-client-0194045282/wedding-management-repo/wedding-api:test"
}

run "validate_cloud_run_configuration" {
  command = plan

  assert {
    condition     = google_cloud_run_v2_service.wedding_api.ingress == "INGRESS_TRAFFIC_ALL"
    error_message = "Ingress do Cloud Run deve ser INGRESS_TRAFFIC_ALL."
  }

  assert {
    condition     = google_cloud_run_v2_service.wedding_api.template[0].containers[0].ports[0].container_port == 8080
    error_message = "Porta do container Cloud Run deve ser 8080."
  }

  assert {
    condition     = google_cloud_run_v2_service_iam_member.public_access.role == "roles/run.invoker"
    error_message = "Servico Cloud Run deve possuir acesso publico roles/run.invoker."
  }
}
