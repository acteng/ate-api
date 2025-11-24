terraform {
  required_providers {
    auth0 = {
      source = "auth0/auth0"
    }
  }
}

resource "auth0_client" "main" {
  name            = var.name
  description     = var.description
  app_type        = "non_interactive"
  grant_types     = ["client_credentials"]
  oidc_conformant = true
}

resource "auth0_client_credentials" "client_secret_post" {
  client_id             = auth0_client.main.client_id
  authentication_method = "client_secret_post"
}

resource "auth0_client_grant" "client_grant" {
  client_id = auth0_client.main.client_id
  audience  = var.audience
  scopes    = []
}

resource "aws_cognito_user_pool_client" "main" {
  name                                 = var.name
  user_pool_id                         = var.user_pool_id
  generate_secret                      = true
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows                  = ["client_credentials"]
  allowed_oauth_scopes                 = var.scopes
  access_token_validity                = 15

  token_validity_units {
    access_token = "minutes"
  }
}
