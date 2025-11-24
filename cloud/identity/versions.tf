terraform {
  required_version = "~> 1.14.0"

  required_providers {
    auth0 = {
      source  = "auth0/auth0"
      version = "~> 1.33.0"
    }

    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.22.0"
    }
  }
}
