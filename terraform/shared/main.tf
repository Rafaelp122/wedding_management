locals {
  gcp_project_id = "gen-lang-client-0194045282"
  gcp_region     = "us-central1"
  github_owner   = "Rafaelp122"
  github_repo    = "wedding_management"

  deployer_email = "github-actions-deployer@${local.gcp_project_id}.iam.gserviceaccount.com"
  runtime_email  = "597398840710-compute@developer.gserviceaccount.com"

  # As permissões atuais são preservadas durante a adoção. O menor privilégio
  # será aplicado somente depois que os três states produzirem planos no-op.
  deployer_project_roles = toset([
    "roles/artifactregistry.admin",
    "roles/cloudbuild.builds.editor",
    "roles/run.admin",
    "roles/storage.admin",
  ])
  runtime_project_roles = toset([
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
    "roles/secretmanager.secretAccessor",
  ])
}

resource "google_storage_bucket" "tfstate" {
  name                        = "${local.gcp_project_id}-tfstate"
  location                    = local.gcp_region
  force_destroy               = false
  public_access_prevention    = "inherited"
  uniform_bucket_level_access = false

  versioning {
    enabled = true
  }

  lifecycle {
    prevent_destroy = true
  }
}

resource "google_artifact_registry_repository" "backend_repo" {
  location      = local.gcp_region
  repository_id = "wedding-management-repo"
  description   = "Imagens OCI do backend Wedding Management"
  format        = "DOCKER"

  lifecycle {
    prevent_destroy = true
  }
}

resource "google_iam_workload_identity_pool" "github_pool" {
  workload_identity_pool_id = "github-pool"
  display_name              = "GitHub Actions Pool"
}

resource "google_iam_workload_identity_pool_provider" "github_provider" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github_pool.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-provider"
  display_name                       = "GitHub Actions Provider"

  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.actor"      = "assertion.actor"
    "attribute.repository" = "assertion.repository"
  }

  # A condição reproduz o provider ativo. Restringir por workflow antes da
  # adoção poderia interromper a autenticação usada para realizar os imports.
  attribute_condition = "assertion.repository == '${local.github_owner}/${local.github_repo}' && assertion.ref in ['refs/heads/main', 'refs/heads/develop']"

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

resource "google_service_account" "github_deployer" {
  account_id   = "github-actions-deployer"
  display_name = "GitHub Actions Deployer"
}

resource "google_service_account_iam_member" "wif_binding" {
  service_account_id = google_service_account.github_deployer.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github_pool.name}/attribute.repository/${local.github_owner}/${local.github_repo}"
}

resource "google_project_iam_member" "deployer" {
  for_each = local.deployer_project_roles

  project = local.gcp_project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.github_deployer.email}"
}

resource "google_project_iam_member" "runtime" {
  for_each = local.runtime_project_roles

  project = local.gcp_project_id
  role    = each.value
  member  = "serviceAccount:${local.runtime_email}"
}

resource "google_service_account_iam_member" "runtime_sa_user" {
  service_account_id = "projects/${local.gcp_project_id}/serviceAccounts/${local.runtime_email}"
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_service_account.github_deployer.email}"
}

resource "vercel_project" "web_app" {
  name           = "wedding-management"
  root_directory = "frontend"

  git_repository = {
    type              = "github"
    repo              = "${local.github_owner}/${local.github_repo}"
    production_branch = "main"
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      oidc_token_config,
      vercel_authentication,
      protection_bypass_for_automation,
    ]
  }
}

resource "vercel_project" "landing" {
  name           = "landing"
  root_directory = "landing"

  git_repository = {
    type              = "github"
    repo              = "${local.github_owner}/${local.github_repo}"
    production_branch = "main"
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      oidc_token_config,
      vercel_authentication,
      protection_bypass_for_automation,
    ]
  }
}
