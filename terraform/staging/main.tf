locals {
  gcp_project_id = "gen-lang-client-0194045282"
  gcp_region     = "us-central1"
  environment    = "staging"

  service_name    = "wedding-backend-staging"
  database_secret = "neon-database-staging" # pragma: allowlist secret
  django_secret   = "django-secret-staging" # pragma: allowlist secret
  r2_bucket_name  = "wedding-management-staging"

  deployer_email = "github-actions-deployer@${local.gcp_project_id}.iam.gserviceaccount.com"
  runtime_email  = "597398840710-compute@developer.gserviceaccount.com"
  secret_accessors = {
    deployer = "serviceAccount:${local.deployer_email}"
  }
}

resource "google_cloud_run_v2_service" "wedding_api" {
  name     = local.service_name
  location = local.gcp_region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account                  = local.runtime_email
    timeout                          = "300s"
    max_instance_request_concurrency = 80

    scaling {
      min_instance_count = 0
      max_instance_count = 20
    }

    containers {
      image = "${data.terraform_remote_state.shared.outputs.artifact_registry_repo_url}/wedding-api:6cc79ee97e64aeb2576ff8e2c114fbeebb660a1d"

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
  secret_id = local.database_secret

  replication {
    auto {}
  }

  lifecycle {
    prevent_destroy = true
  }
}

resource "google_secret_manager_secret" "django" {
  secret_id = local.django_secret

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
  name       = local.r2_bucket_name

  lifecycle {
    prevent_destroy = true
  }
}

resource "vercel_project_environment_variable" "web_app_api_url" {
  project_id = data.terraform_remote_state.shared.outputs.web_app_project_id
  key        = "VITE_API_URL"
  value      = google_cloud_run_v2_service.wedding_api.uri
  target     = ["preview"]
  git_branch = "develop"
}
