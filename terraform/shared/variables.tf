variable "vercel_api_token" {
  type        = string
  description = "Token da Vercel usado somente durante operações Terraform"
  sensitive   = true
}

variable "vercel_team_id" {
  type        = string
  description = "ID do time proprietário dos projetos Vercel"
}
