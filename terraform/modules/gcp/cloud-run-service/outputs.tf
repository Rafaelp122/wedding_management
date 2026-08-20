output "service_uri" {
  description = "URI pública do serviço Cloud Run"
  value       = google_cloud_run_v2_service.wedding_api.uri
}

output "service_name" {
  description = "Nome do serviço Cloud Run"
  value       = google_cloud_run_v2_service.wedding_api.name
}

output "database_secret_id" {
  description = "ID do segredo do banco de dados no Secret Manager"
  value       = google_secret_manager_secret.database.secret_id
}

output "django_secret_id" {
  description = "ID do segredo do Django no Secret Manager"
  value       = google_secret_manager_secret.django.secret_id
}

output "email_smtp_password_secret_id" {
  description = "ID do segredo da senha/API key SMTP no Secret Manager"
  value       = google_secret_manager_secret.email_smtp_password.secret_id
}

output "r2_bucket_name" {
  description = "Nome do bucket R2 criado/gerenciado"
  value       = cloudflare_r2_bucket.contracts.name
}
