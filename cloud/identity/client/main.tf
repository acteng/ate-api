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

resource "azuread_application" "main" {
  display_name = "${var.name} (${var.env})"
  description  = var.description
  owners       = [var.owner]

  api {
    requested_access_token_version = 2
  }

  password {
    display_name = "Client secret"
  }
}

resource "azuread_service_principal" "main" {
  client_id = azuread_application.main.client_id
  owners    = [var.owner]

  feature_tags {
    enterprise = true
  }
}
