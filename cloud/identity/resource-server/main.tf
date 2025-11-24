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

# resource "random_uuid" "app_role_id" {
# }

resource "azuread_application" "main" {
  display_name    = "ATE API (${var.env})"
  owners          = [var.owner]
  identifier_uris = [var.identifier]

  api {
    requested_access_token_version = 2
  }

  # app_role {
  #   id                   = random_uuid.app_role_id.result
  #   display_name         = "Default role"
  #   description          = "Default role"
  #   allowed_member_types = ["Application"]
  #   value                = "Default"
  # }
}

resource "azuread_service_principal" "main" {
  client_id = azuread_application.main.client_id
  owners    = [var.owner]

  feature_tags {
    enterprise = true
  }
}
