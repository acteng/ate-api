terraform {
  required_providers {
    auth0 = {
      source = "auth0/auth0"
    }
  }
}

resource "auth0_resource_server" "server" {
  name       = "ATE API"
  identifier = var.identifier
}
