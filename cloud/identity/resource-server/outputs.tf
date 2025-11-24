# TODO: output tolist(azuread_application.main.identifier_uris)[0]
output "identifier" {
  description = "Resource server identifier"
  value       = auth0_resource_server.server.identifier
}

output "application_id" {
  description = "Resource server application client ID"
  value       = azuread_application.main.client_id
}

output "service_principal_id" {
  description = "Resource server service principal object ID"
  value       = azuread_service_principal.main.object_id
}

# output "app_role_id" {
#   description = "Default role ID"
#   value       = azuread_application.main.app_role_ids["Default"]
# }
