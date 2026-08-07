output "cloud_run_url" {
  description = "URL pública do backend Cloud Run produção"
  value       = module.backend_service.service_uri
}

output "r2_bucket_name" {
  description = "Nome do bucket R2 produção"
  value       = module.backend_service.r2_bucket_name
}
