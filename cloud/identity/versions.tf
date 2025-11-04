terraform {
  required_version = "~> 1.13.0"

  required_providers {
    auth0 = {
      source  = "auth0/auth0"
      version = "~> 1.33.0"
    }
  }
}
