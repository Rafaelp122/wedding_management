# terraform/gcp_cloud_run.tf
# Provisionamento do Google Artifact Registry e do Serviço Serverless Google Cloud Run v2 (ADR-001).

# Repositório no Artifact Registry para imagens OCI Docker do Backend
resource "google_artifact_registry_repository" "backend_repo" {
  location      = var.gcp_region
  repository_id = "wedding-management-repo"
  description   = "Repositório Docker para imagens OCI do Backend Django Ninja"
  format        = "DOCKER"

  cleanup_policies {
    id     = "keep-recent-images"
    action = "KEEP"
    most_recent_versions {
      keep_count = 5
    }
  }
}

# Serviço Cloud Run v2 executando o container Django Ninja
resource "google_cloud_run_v2_service" "wedding_api" {
  name     = var.environment == "production" ? "wedding-api" : "wedding-api-${var.environment}"
  location = var.gcp_region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    scaling {
      min_instance_count = 0
      max_instance_count = 5
    }

    containers {
      image = "${var.gcp_region}-docker.pkg.dev/${var.gcp_project_id}/${google_artifact_registry_repository.backend_repo.repository_id}/wedding-api:latest"

      resources {
        limits = {
          cpu    = "1000m"
          memory = "512Mi"
        }
      }

      ports {
        container_port = 8000
      }

      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }
    }
  }

  lifecycle {
    ignore_changes = [
      template[0].containers[0].image,
    ]
  }
}

# Permissão de invocação pública na API (acessível pelo frontend/clientes)
resource "google_cloud_run_v2_service_iam_member" "public_access" {
  location = google_cloud_run_v2_service.wedding_api.location
  name     = google_cloud_run_v2_service.wedding_api.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Exemplo de Bloco de Importação (para adotar serviço Cloud Run existente)
# import {
#   to = google_cloud_run_v2_service.wedding_api
#   id = "projects/${var.gcp_project_id}/locations/${var.gcp_region}/services/wedding-api"
# }
