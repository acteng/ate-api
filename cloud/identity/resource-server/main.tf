terraform {
  required_providers {
    auth0 = {
      source = "auth0/auth0"
    }
  }
}

locals {
  minute_in_seconds = 60
}

resource "auth0_resource_server" "server" {
  name           = "ATE API"
  identifier     = var.identifier
  token_lifetime = 15 * local.minute_in_seconds
}

resource "aws_cognito_resource_server" "main" {
  name         = "ATE API"
  identifier   = var.identifier
  user_pool_id = var.user_pool_id
}
