output "cloud_run_url" {
  description = "URL pública do backend Cloud Run staging"
  value       = module.backend_service.service_uri
}

output "r2_bucket_name" {
  description = "Nome do bucket R2 staging"
  value       = module.backend_service.r2_bucket_name
}
