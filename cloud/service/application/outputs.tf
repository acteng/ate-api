output "name" {
  description = "Cloud Run service name"
  value       = google_cloud_run_v2_service.ate_api.name
}

output "service_account_id" {
  description = "Cloud Run service account ID"
  value       = google_service_account.cloud_run_ate_api.id
}
