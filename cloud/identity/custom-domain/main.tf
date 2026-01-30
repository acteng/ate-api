terraform {
  required_providers {
    auth0 = {
      source = "auth0/auth0"
    }
  }
}

resource "auth0_custom_domain" "main" {
  domain = var.domain
  type   = "auth0_managed_certs"
}
