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

data "auth0_tenant" "main" {
}

data "azuread_client_config" "main" {
}

module "resource_server" {
  source     = "./resource-server"
  identifier = local.config[local.env].resource_server_identifier
}

module "example_client" {
  source      = "./client"
  name        = "Example"
  env         = local.env
  description = "Client used for API development."
  owner       = data.azuread_client_config.main.object_id
  audience    = module.resource_server.identifier
}

module "update_your_capital_schemes_client" {
  source      = "./client"
  name        = "Update your capital schemes"
  env         = local.env
  description = "Client used for the Update your capital schemes service."
  owner       = data.azuread_client_config.main.object_id
  audience    = module.resource_server.identifier
}
