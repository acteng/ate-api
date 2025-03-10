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
