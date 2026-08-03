# terraform/environments/staging.tfvars
# Configurações parametrizadas para o Ambiente de Homologação (Staging).

environment      = "staging"
gcp_project_id   = "gen-lang-client-0194045282"
gcp_region       = "us-central1"
github_owner     = "Rafaelp122"
github_repo_name = "wedding_management"

allowed_frontend_origins = [
  "https://wedding-web-app-staging.vercel.app",
  "https://wedding-landing-staging.vercel.app"
]
