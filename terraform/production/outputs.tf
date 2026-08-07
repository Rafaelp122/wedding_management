output "r2_bucket_name" {
  description = "Nome do bucket R2 produção"
  value       = module.backend_service.r2_bucket_name
}
