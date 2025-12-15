terraform {
  required_version = "~> 1.14.0"

  required_providers {
    auth0 = {
      source  = "auth0/auth0"
      version = "~> 1.36.0"
    }
  }
}
