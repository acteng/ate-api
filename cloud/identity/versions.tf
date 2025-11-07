terraform {
  required_version = "~> 1.14.0"

  required_providers {
    auth0 = {
      source  = "auth0/auth0"
      version = "~> 1.33.0"
    }

    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 3.7.0"
    }
  }
}
