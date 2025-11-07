output "client_id" {
  description = "OAuth client ID"
  value       = azuread_application.main.client_id
}

output "client_secret" {
  description = "OAuth client secret"
  value       = tolist(azuread_application.main.password)[0].value
  sensitive   = true
}
