# terraform/gcp_iam.tf
# Configuração de autenticação segura via Workload Identity Federation (WIF)
# permitindo que o GitHub Actions acesse a GCP sem chaves estáticas (ADR-001 / ci-cd-pipeline-flow.md).

# Workload Identity Pool para o GitHub
resource "google_iam_workload_identity_pool" "github_pool" {
  workload_identity_pool_id = "github-actions-pool"
  display_name              = "GitHub Actions Pool"
  description               = "Pool de identidade federada para CI/CD do GitHub Actions"
}

# Provider OIDC do GitHub no Pool
resource "google_iam_workload_identity_pool_provider" "github_provider" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github_pool.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-actions-provider"
  display_name                       = "GitHub Actions Provider"
  description                        = "Provedor OIDC para autenticação do repositório GitHub"

  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.actor"      = "assertion.actor"
    "attribute.repository" = "assertion.repository"
  }

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

# Service Account dedicada para os Deploys do CI/CD
resource "google_service_account" "github_deployer" {
  account_id   = "github-actions-deployer"
  display_name = "GitHub Actions Deployer Service Account"
  description  = "Conta de serviço utilizada pela pipeline de CI/CD para deploy no Cloud Run e Artifact Registry"
}

# Permissão para o GitHub Actions representar a Service Account via WIF
resource "google_service_account_iam_member" "wif_binding" {
  service_account_id = google_service_account.github_deployer.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github_pool.name}/attribute.repository/${var.github_owner}/${var.github_repo_name}"
}

# Atribuição de permissões mínimas (Princípio do Menor Privilégio)
resource "google_project_iam_member" "cloud_run_admin" {
  project = var.gcp_project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${google_service_account.github_deployer.email}"
}

resource "google_project_iam_member" "artifact_registry_writer" {
  project = var.gcp_project_id
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${google_service_account.github_deployer.email}"
}

resource "google_project_iam_member" "sa_user" {
  project = var.gcp_project_id
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${google_service_account.github_deployer.email}"
}

# Exemplo de Bloco de Importação (para adotar Service Account existente se já criada no console)
# import {
#   to = google_service_account.github_deployer
#   id = "projects/${var.gcp_project_id}/serviceAccounts/github-actions-deployer@${var.gcp_project_id}.iam.gserviceaccount.com"
# }
