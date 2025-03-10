output "resource_server_identifier" {
  description = "Resource server identifier"
  value       = module.resource_server.identifier
}

output "ate_client_id" {
  description = "ATE client ID"
  value       = module.ate_client.client_id
}

output "ate_client_secret" {
  description = "ATE client secret"
  value       = module.ate_client.client_secret
  sensitive   = true
}
