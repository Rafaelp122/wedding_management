output "cloud_run_url" {
  description = "URL do backend de staging"
  value       = google_cloud_run_v2_service.wedding_api.uri
}

output "r2_bucket_name" {
  description = "Bucket R2 isolado de staging"
  value       = cloudflare_r2_bucket.contracts.name
}
