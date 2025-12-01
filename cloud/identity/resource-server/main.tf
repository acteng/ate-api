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

moved {
  from = auth0_resource_server.server
  to   = auth0_resource_server.main
}

resource "auth0_resource_server" "main" {
  name           = "ATE API"
  identifier     = var.identifier
  token_lifetime = 15 * local.minute_in_seconds
}
