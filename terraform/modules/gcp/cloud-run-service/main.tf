locals {
  secret_accessors = {
    deployer = "serviceAccount:${var.deployer_email}"
  }
}

resource "google_cloud_run_v2_service" "wedding_api" {
  name     = var.service_name
  location = var.gcp_region
  ingress  = "INGRESS_TRAFFIC_ALL"

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

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      client,
      client_version,
      template[0].containers[0].env,
      template[0].containers[0].image,
      template[0].containers[0].resources,
      template[0].containers[0].startup_probe,
      template[0].labels,
    ]
  }
}

resource "google_cloud_run_v2_service_iam_member" "public_access" {
  location = google_cloud_run_v2_service.wedding_api.location
  name     = google_cloud_run_v2_service.wedding_api.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_secret_manager_secret" "database" {
  secret_id = var.database_secret_id # pragma: allowlist secret

  replication {
    auto {}
  }

  lifecycle {
    prevent_destroy = true
  }
}

resource "google_secret_manager_secret" "django" {
  secret_id = var.django_secret_id # pragma: allowlist secret

  replication {
    auto {}
  }

  lifecycle {
    prevent_destroy = true
  }
}

resource "google_secret_manager_secret_iam_member" "database_access" {
  for_each = local.secret_accessors

  secret_id = google_secret_manager_secret.database.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = each.value
}

resource "google_secret_manager_secret_iam_member" "django_access" {
  for_each = local.secret_accessors

  secret_id = google_secret_manager_secret.django.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = each.value
}

resource "cloudflare_r2_bucket" "contracts" {
  account_id = var.cloudflare_account_id
  name       = var.r2_bucket_name

  lifecycle {
    prevent_destroy = true
  }
}

resource "vercel_project_environment_variable" "web_app_api_url" {
  project_id = var.web_app_project_id
  key        = "VITE_API_URL"
  value      = google_cloud_run_v2_service.wedding_api.uri
  target     = var.vercel_target
  git_branch = var.vercel_git_branch
}
