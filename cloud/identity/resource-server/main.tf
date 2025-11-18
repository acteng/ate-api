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

resource "azuread_application" "main" {
  display_name    = "ATE API (${var.env})"
  owners          = [var.owner]
  identifier_uris = [var.identifier]
}
