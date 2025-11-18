# See: https://learn.microsoft.com/en-us/entra/identity-platform/v2-protocols-oidc#find-your-apps-openid-configuration-document-uri
output "oidc_server_metadata_url" {
  description = "OIDC configuration URL"
  value       = "https://login.microsoftonline.com/${data.azuread_client_config.main.tenant_id}/v2.0/.well-known/openid-configuration"
}

output "resource_server_identifier" {
  description = "Resource server identifier"
  value       = module.resource_server.identifier
}

output "resource_server_application_id" {
  description = "Resource server application ID"
  value       = module.resource_server.application_id
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

output "update_your_capital_schemes_client_id" {
  description = "Update your capital schemes client ID"
  value       = module.update_your_capital_schemes_client.client_id
}

output "update_your_capital_schemes_client_secret" {
  description = "Update your capital schemes client secret"
  value       = module.update_your_capital_schemes_client.client_secret
  sensitive   = true
}
