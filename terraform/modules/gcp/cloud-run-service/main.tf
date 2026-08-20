locals {
  # Concede acesso de leitura aos segredos tanto para o deployer (CI/CD) quanto para a runtime SA do Cloud Run.
  secret_accessors = {
    deployer = "serviceAccount:${var.deployer_email}"
    runtime  = "serviceAccount:${var.runtime_email}"
  }
}

# Servico Cloud Run v2 responsável por hospedar a API REST (Django Ninja).
resource "google_cloud_run_v2_service" "wedding_api" {
  name     = var.service_name
  location = var.gcp_region
  ingress  = "INGRESS_TRAFFIC_ALL"

  labels = {
    environment = var.environment
  }

  template {
    service_account                  = var.runtime_email
    timeout                          = "300s"
    max_instance_request_concurrency = var.max_concurrency

    scaling {
      min_instance_count = 0
      max_instance_count = 20
    }

    containers {
      image = var.initial_image

      resources {
        limits = {
          cpu    = "1000m"
          memory = "512Mi"
        }
      }

      ports {
        container_port = 8080
      }
    }
  }

  # O CD do projeto (GitHub Actions/Cloud Build) atualiza imagens, variaveis de ambiente e recursos.
  # ignore_changes evita que o Terraform reverta deployments de producao/staging para a imagem inicial.
  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      client,
      client_version,
      labels,
      template[0].containers[0].env,
      template[0].containers[0].image,
      template[0].containers[0].resources,
      template[0].containers[0].startup_probe,
      template[0].labels,
    ]
  }
}

# Concede permissao de invocacao publica para o Cloud Run.
resource "google_cloud_run_v2_service_iam_member" "public_access" {
  location = google_cloud_run_v2_service.wedding_api.location
  name     = google_cloud_run_v2_service.wedding_api.name
  role     = "roles/run.invoker"
  member   = "allUsers"

  lifecycle {
    prevent_destroy = true
  }
}

# Container do segredo de banco de dados no Secret Manager (conforme ADR-025, a payload e gerida fora do Terraform).
resource "google_secret_manager_secret" "database" {
  secret_id = var.database_secret_id # pragma: allowlist secret

  labels = {
    environment = var.environment
  }

  replication {
    auto {}
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      labels,
    ]
  }
}

# Container do segredo Django no Secret Manager.
resource "google_secret_manager_secret" "django" {
  secret_id = var.django_secret_id # pragma: allowlist secret

  labels = {
    environment = var.environment
  }

  replication {
    auto {}
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      labels,
    ]
  }
}

# Concede acesso de leitura ao segredo do banco de dados para deployer e runtime SA.
resource "google_secret_manager_secret_iam_member" "database_access" {
  for_each = local.secret_accessors

  secret_id = google_secret_manager_secret.database.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = each.value
}

# Concede acesso de leitura ao segredo Django para deployer e runtime SA.
resource "google_secret_manager_secret_iam_member" "django_access" {
  for_each = local.secret_accessors

  secret_id = google_secret_manager_secret.django.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = each.value
}

# Container do segredo do usuário SMTP no Secret Manager.
resource "google_secret_manager_secret" "email_smtp_user" {
  secret_id = var.email_smtp_user_secret_id # pragma: allowlist secret

  labels = {
    environment = var.environment
  }

  replication {
    auto {}
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      labels,
    ]
  }
}

# Container do segredo da senha/API key SMTP no Secret Manager.
resource "google_secret_manager_secret" "email_smtp_password" {
  secret_id = var.email_smtp_password_secret_id # pragma: allowlist secret

  labels = {
    environment = var.environment
  }

  replication {
    auto {}
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      labels,
    ]
  }
}

# Concede acesso de leitura ao segredo de usuário SMTP para deployer e runtime SA.
resource "google_secret_manager_secret_iam_member" "email_smtp_user_access" {
  for_each = local.secret_accessors

  secret_id = google_secret_manager_secret.email_smtp_user.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = each.value
}

# Concede acesso de leitura ao segredo de senha SMTP para deployer e runtime SA.
resource "google_secret_manager_secret_iam_member" "email_smtp_password_access" {
  for_each = local.secret_accessors

  secret_id = google_secret_manager_secret.email_smtp_password.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = each.value
}

# Bucket de arquivos de contrato no Cloudflare R2 (ADR-004).
resource "cloudflare_r2_bucket" "contracts" {
  account_id = var.cloudflare_account_id
  name       = var.r2_bucket_name

  lifecycle {
    prevent_destroy = true
  }
}

# Variavel de ambiente VITE_API_URL sincronizada com o projeto Vercel.
resource "vercel_project_environment_variable" "web_app_api_url" {
  project_id = var.web_app_project_id
  key        = "VITE_API_URL"
  value      = google_cloud_run_v2_service.wedding_api.uri
  target     = var.vercel_target
  git_branch = var.vercel_git_branch
}
