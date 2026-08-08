mock_provider "google" {}
mock_provider "cloudflare" {}
mock_provider "vercel" {}

variables {
  environment           = "staging"
  service_name          = "wedding-backend-staging"
  database_secret_id    = "neon-database-staging"
  django_secret_id      = "django-secret-staging"
  r2_bucket_name        = "wedding-management-staging"
  cloudflare_account_id = "dummy-cloudflare-account-id"
  deployer_email        = "deployer@example.com"
  runtime_email         = "runtime@example.com"
  web_app_project_id    = "prj_dummy_web_app"
  vercel_target         = ["preview"]
  vercel_git_branch     = "develop"
  initial_image         = "us-central1-docker.pkg.dev/dummy-project/wedding-repo/wedding-api:test"
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
    error_message = "Serviço Cloud Run deve possuir acesso público roles/run.invoker."
  }

  assert {
    condition     = google_secret_manager_secret_iam_member.database_access["runtime"].role == "roles/secretmanager.secretAccessor"
    error_message = "A Service Account de runtime deve possuir role secretAccessor no banco de dados."
  }

  assert {
    condition     = google_secret_manager_secret_iam_member.django_access["runtime"].role == "roles/secretmanager.secretAccessor"
    error_message = "A Service Account de runtime deve possuir role secretAccessor no Django."
  }

  assert {
    condition     = google_secret_manager_secret_iam_member.database_access["deployer"].role == "roles/secretmanager.secretAccessor"
    error_message = "A Service Account do deployer deve possuir role secretAccessor no banco de dados."
  }

  assert {
    condition     = google_secret_manager_secret_iam_member.django_access["deployer"].role == "roles/secretmanager.secretAccessor"
    error_message = "A Service Account do deployer deve possuir role secretAccessor no Django."
  }
}

run "validate_invalid_environment_rejection" {
  command = plan

  variables {
    environment = "invalid-env"
  }

  expect_failures = [
    var.environment,
  ]
}

run "validate_custom_concurrency_propagation" {
  command = plan

  variables {
    max_concurrency = 15
  }

  assert {
    condition     = google_cloud_run_v2_service.wedding_api.template[0].max_instance_request_concurrency == 15
    error_message = "A concorrência customizada deve ser propagada para a template do Cloud Run."
  }
}

run "validate_tasks_backend_propagation" {
  command = plan

  variables {
    tasks_backend = "immediate"
  }

  assert {
    condition     = var.tasks_backend == "immediate"
    error_message = "A variável tasks_backend deve ser aceita e validada."
  }
}
