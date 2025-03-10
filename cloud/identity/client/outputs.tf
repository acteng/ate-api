output "client_id" {
  description = "OAuth client ID"
  value       = auth0_client.main.client_id
}

output "client_secret" {
  description = "OAuth client secret"
  value       = auth0_client_credentials.client_secret_post.client_secret
  sensitive   = true
}
