variable "cloudflare_account_id" {
  type        = string
  description = "Account ID da Cloudflare proprietária do bucket R2"
}

variable "cloudflare_api_token" {
  type        = string
  description = "Token Cloudflare com acesso ao R2"
  sensitive   = true
}

variable "vercel_api_token" {
  type        = string
  description = "Token da Vercel usado somente durante operações Terraform"
  sensitive   = true
}

variable "vercel_team_id" {
  type        = string
  description = "ID do time proprietário do projeto Vercel"
}
