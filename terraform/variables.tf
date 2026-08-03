# terraform/variables.tf
# Definição de variáveis de ambiente e parâmetros de infraestrutura.

variable "gcp_project_id" {
  type        = string
  description = "ID do projeto na Google Cloud Platform (GCP)"
  default     = "gen-lang-client-0194045282"
}

variable "gcp_region" {
  type        = string
  description = "Região principal do GCP para provisionamento de recursos"
  default     = "us-central1"
}

variable "environment" {
  type        = string
  description = "Ambiente de execução (production, staging, dev)"
  default     = "production"
}

variable "github_owner" {
  type        = string
  description = "Organização ou proprietário do repositório no GitHub"
  default     = "Rafaelp122"
}

variable "github_repo_name" {
  type        = string
  description = "Nome do repositório no GitHub"
  default     = "wedding_management"
}

variable "allowed_frontend_origins" {
  type        = list(string)
  description = "Lista de origens (domínios) permitidas no CORS do Cloudflare R2"
  default     = []
}

variable "cloudflare_account_id" {
  type        = string
  description = "Account ID da conta no Cloudflare para o R2 Storage"
  default     = ""
  sensitive   = true
}

variable "cloudflare_api_token" {
  type        = string
  description = "API Token do Cloudflare com permissões de administração do R2"
  default     = ""
  sensitive   = true
}

variable "vercel_api_token" {
  type        = string
  description = "API Token da Vercel para gerenciamento de projetos e variáveis"
  default     = ""
  sensitive   = true
}

variable "vercel_team_id" {
  type        = string
  description = "ID do Team na Vercel (opcional se for conta pessoal)"
  default     = ""
}

variable "github_token" {
  type        = string
  description = "Personal Access Token (PAT) do GitHub para gerenciamento de secrets no repositório"
  default     = ""
  sensitive   = true
}
