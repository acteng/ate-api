output "url" {
  description = "Application service URL"
  value       = module.application.url
}

output "github_action_deploy_private_key" {
  description = "Service account key for deploy GitHub Action service account"
  value       = module.github_action_deploy.private_key
  sensitive   = true
}
