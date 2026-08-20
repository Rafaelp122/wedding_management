variable "environment" {
  description = "Nome do ambiente (staging ou production)"
  type        = string

  validation {
    condition     = contains(["staging", "production"], var.environment)
    error_message = "O ambiente deve ser staging ou production."
  }
}

variable "service_name" {
  description = "Nome do serviço Cloud Run"
  type        = string
}

variable "gcp_region" {
  description = "Região do serviço no GCP"
  type        = string
  default     = "us-central1"
}

variable "database_secret_id" {
  description = "ID do segredo do banco de dados no Secret Manager"
  type        = string
}

variable "django_secret_id" {
  description = "ID do segredo da chave Django no Secret Manager"
  type        = string
}

variable "email_smtp_user_secret_id" {
  description = "ID do segredo do usuário SMTP no Secret Manager"
  type        = string
}

variable "email_smtp_password_secret_id" {
  description = "ID do segredo da senha/API key SMTP no Secret Manager"
  type        = string
}

variable "r2_bucket_name" {
  description = "Nome do bucket R2 no Cloudflare"
  type        = string
}

variable "cloudflare_account_id" {
  description = "Account ID do Cloudflare"
  type        = string
}

variable "deployer_email" {
  description = "Email da Service Account do deployer"
  type        = string
}

variable "runtime_email" {
  description = "Email da Service Account de runtime"
  type        = string
}

variable "web_app_project_id" {
  description = "ID do projeto web app na Vercel"
  type        = string
}

variable "vercel_target" {
  description = "Target da variável de ambiente na Vercel (preview ou production)"
  type        = list(string)
}

variable "vercel_git_branch" {
  description = "Branch associada na Vercel (opcional)"
  type        = string
  default     = null
}

variable "initial_image" {
  description = "Imagem OCI de referência inicial para o Cloud Run"
  type        = string
}

variable "max_concurrency" {
  description = "Concorrência máxima de requisições por instância"
  type        = number
  default     = 80
}

variable "tasks_backend" {
  description = "Tipo de backend de tarefas (db, immediate, valkey, etc.)"
  type        = string
  default     = "db"
}
