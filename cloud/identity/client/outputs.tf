output "client_id" {
  description = "OAuth client ID"
  value       = aws_cognito_user_pool_client.main.id
}

output "client_secret" {
  description = "OAuth client secret"
  value       = aws_cognito_user_pool_client.main.client_secret
  sensitive   = true
}
