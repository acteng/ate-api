output "url" {
  description = "Load balancer URL"
  value       = module.load_balancer.url
}

output "ip_address" {
  description = "Load balancer IP address"
  value       = module.load_balancer.ip_address
}

output "github_action_deploy_private_key" {
  description = "Service account key for deploy GitHub Action service account"
  value       = length(module.github_action_deploy) > 0 ? module.github_action_deploy[0].private_key : null
  sensitive   = true
}
