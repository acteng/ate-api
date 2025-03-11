output "oidc_server_metadata_url" {
  description = "OIDC configuration URL"
  value       = "https://${data.auth0_tenant.main.domain}/.well-known/openid-configuration"
}

output "resource_server_identifier" {
  description = "Resource server identifier"
  value       = module.resource_server.identifier
}

output "example_client_id" {
  description = "Example client ID"
  value       = module.example_client.client_id
}

output "example_client_secret" {
  description = "Example client secret"
  value       = module.example_client.client_secret
  sensitive   = true
}
