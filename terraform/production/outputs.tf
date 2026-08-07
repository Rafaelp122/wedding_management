output "cloud_run_url" {
  description = "URL do backend de produção"
  value       = google_cloud_run_v2_service.wedding_api.uri
}

output "r2_bucket_name" {
  description = "Bucket R2 de produção"
  value       = cloudflare_r2_bucket.contracts.name
}
