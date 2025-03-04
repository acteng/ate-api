output "url" {
  description = "Application service URL"
  value       = google_cloud_run_v2_service.ate_api.uri
}
