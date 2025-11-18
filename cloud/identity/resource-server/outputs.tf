# TODO: output tolist(azuread_application.main.identifier_uris)[0]
output "identifier" {
  description = "Resource server identifier"
  value       = auth0_resource_server.server.identifier
}

output "application_id" {
  description = "Resource server application client ID"
  value       = azuread_application.main.client_id
}
