# terraform/vercel.tf
# Gerenciamento declarativo de Projetos e Variáveis de Ambiente na Vercel (ci-cd-pipeline-flow.md).

# Projeto Vercel: Aplicação Web Frontend React + Vite
resource "vercel_project" "web_app" {
  name      = "wedding-web-app"
  framework = "vite"

  git_repository = {
    type = "github"
    repo = "${var.github_owner}/${var.github_repo_name}"
  }

  root_directory = "frontend"
}

# Injeção automática da URL do Cloud Run na variável VITE_API_URL do aplicativo React
resource "vercel_project_environment_variable" "web_app_api_url" {
  project_id = vercel_project.web_app.id
  key        = "VITE_API_URL"
  value      = google_cloud_run_v2_service.wedding_api.uri
  target     = ["production", "preview"]
}

# Projeto Vercel: Landing Page Astro
resource "vercel_project" "landing" {
  name      = "wedding-landing"
  framework = "astro"

  git_repository = {
    type = "github"
    repo = "${var.github_owner}/${var.github_repo_name}"
  }

  root_directory = "landing"
}

# Injeção automática da URL do Cloud Run na variável PUBLIC_API_URL da Landing Page
resource "vercel_project_environment_variable" "landing_api_url" {
  project_id = vercel_project.landing.id
  key        = "PUBLIC_API_URL"
  value      = google_cloud_run_v2_service.wedding_api.uri
  target     = ["production", "preview"]
}

# Exemplo de Bloco de Importação (para adotar projetos existentes da Vercel)
# import {
#   to = vercel_project.web_app
#   id = "prj_xxxxxxxxxxxxxxxxx"
# }
