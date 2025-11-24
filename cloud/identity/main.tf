terraform {
  backend "gcs" {
    bucket = "dft-ate-api-common-tf-backend"
    prefix = "identity"
  }
}

provider "aws" {
  region = "eu-west-2"
}

locals {
  env                    = terraform.workspace
  resource_server_domain = "api.activetravelengland.gov.uk"

  config = {
    dev = {
      resource_server_identifier = "https://dev.${local.resource_server_domain}"
    }
    test = {
      resource_server_identifier = "https://test.${local.resource_server_domain}"
    }
    prod = {
      resource_server_identifier = "https://${local.resource_server_domain}"
    }
  }
}

data "auth0_tenant" "main" {
}

resource "aws_cognito_user_pool" "main" {
  name = "ate-api"
}

module "resource_server" {
  source     = "./resource-server"
  identifier = local.config[local.env].resource_server_identifier
}

module "example_client" {
  source       = "./client"
  name         = "Example"
  description  = "Client used for API development."
  audience     = module.resource_server.identifier
  user_pool_id = aws_cognito_user_pool.main.id
}

module "update_your_capital_schemes_client" {
  source       = "./client"
  name         = "Update your capital schemes"
  description  = "Client used for the Update your capital schemes service."
  audience     = module.resource_server.identifier
  user_pool_id = aws_cognito_user_pool.main.id
}
