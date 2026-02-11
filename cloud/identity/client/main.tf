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

  jwt_configuration {
    alg = "RS256"
  }
}

resource "auth0_client_credentials" "private_key_jwt" {
  client_id             = auth0_client.main.client_id
  authentication_method = "private_key_jwt"

  private_key_jwt {
    credentials {
      credential_type = "public_key"
      pem             = var.public_key
    }
  }
}

resource "auth0_client_grant" "client_grant" {
  client_id = auth0_client.main.client_id
  audience  = var.audience
  scopes    = []
}
