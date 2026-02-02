terraform {
  backend "gcs" {
    bucket = "dft-ate-api-common-tf-backend"
    prefix = "identity"
  }
}

locals {
  env                    = terraform.workspace
  domain                 = "identity.api.activetravelengland.gov.uk"
  resource_server_domain = "api.activetravelengland.gov.uk"

  config = {
    dev = {
      domain                     = "dev.${local.domain}"
      resource_server_identifier = "https://dev.${local.resource_server_domain}"
    }
    test = {
      domain                     = "test.${local.domain}"
      resource_server_identifier = "https://test.${local.resource_server_domain}"
    }
    prod = {
      domain                     = local.domain
      resource_server_identifier = "https://${local.resource_server_domain}"
    }
  }
}

module "custom_domain" {
  source = "./custom-domain"
  domain = local.config[local.env].domain
}

module "resource_server" {
  source     = "./resource-server"
  identifier = local.config[local.env].resource_server_identifier
}

module "example_client" {
  source      = "./client"
  name        = "Example"
  description = "Client used for API development."
  audience    = module.resource_server.identifier
}

module "update_your_capital_schemes_client" {
  source      = "./client"
  name        = "Update your capital schemes"
  description = "Client used for the Update your capital schemes service."
  audience    = module.resource_server.identifier
}
