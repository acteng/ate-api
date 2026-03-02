output "record" {
  description = "DNS record required to verify the custom domain"
  value       = module.custom_domain.record
}

output "oidc_server_metadata_url" {
  description = "Authorisation server configuration endpoint"
  value       = "https://${module.custom_domain.domain}/.well-known/openid-configuration"
}

output "issuer" {
  description = "Authorisation server issuer"
  value       = "https://${module.custom_domain.domain}/"
}

output "resource_server_identifier" {
  description = "Resource server identifier"
  value       = module.resource_server.identifier
}

output "example_client_id" {
  description = "Example client ID"
  value       = module.example_client.client_id
}

output "update_your_capital_schemes_client_id" {
  description = "Update your capital schemes client ID"
  value       = module.update_your_capital_schemes_client.client_id
}
