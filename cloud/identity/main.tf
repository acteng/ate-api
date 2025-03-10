terraform {
  backend "gcs" {
    bucket = "dft-ate-api-common-tf-backend"
    prefix = "identity"
  }
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

module "resource_server" {
  source     = "./resource-server"
  identifier = local.config[local.env].resource_server_identifier
}

module "ate_client" {
  source      = "./client"
  name        = "ATE"
  description = "Client used for API development."
  audience    = module.resource_server.identifier
}
