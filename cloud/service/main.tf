terraform {
  backend "gcs" {
    bucket = "dft-ate-api-common-tf-backend"
    prefix = "service"
  }
}

provider "google" {
  project = local.project
}

locals {
  env     = terraform.workspace
  project = "${var.project_prefix}-${local.env}"
  domain  = "api.activetravelengland.gov.uk"

  config = {
    dev = {
      image_tag            = "latest"
      keep_idle            = false
      docs_auth            = true
      monitoring           = false
      domain               = "dev.${local.domain}"
      github_action_deploy = true
    }
    test = {
      image_tag            = "0.18.0"
      keep_idle            = false
      docs_auth            = true
      monitoring           = false
      domain               = "test.${local.domain}"
      github_action_deploy = false
    }
    prod = {
      image_tag            = "0.18.0"
      keep_idle            = true
      docs_auth            = true
      monitoring           = true
      domain               = local.domain
      github_action_deploy = false
    }
  }
}

data "terraform_remote_state" "docker_repository" {
  backend = "gcs"
  config = {
    bucket = "${var.project_prefix}-common-tf-backend"
    prefix = "docker-repository"
  }
}

data "terraform_remote_state" "schemes_database" {
  backend = "gcs"
  config = {
    bucket = "${var.database_project_prefix}-common-tf-backend"
    prefix = "schemes-database"
  }
  workspace = local.env
}

data "terraform_remote_state" "identity" {
  backend = "gcs"
  config = {
    bucket = "${var.project_prefix}-common-tf-backend"
    prefix = "identity"
  }
  workspace = local.env
}

resource "google_project_service" "run" {
  project = local.project
  service = "run.googleapis.com"
}

resource "google_project_service" "secret_manager" {
  project = local.project
  service = "secretmanager.googleapis.com"
}

resource "google_project_service" "sql_admin" {
  project = local.project
  service = "sqladmin.googleapis.com"
}

module "application" {
  source                     = "./application"
  project                    = local.project
  region                     = var.location
  docker_repository_project  = data.terraform_remote_state.docker_repository.outputs.project
  docker_repository_url      = data.terraform_remote_state.docker_repository.outputs.url
  image_tag                  = local.config[local.env].image_tag
  database_project           = data.terraform_remote_state.schemes_database.outputs.project
  database_connection_name   = data.terraform_remote_state.schemes_database.outputs.connection_name
  database_name              = data.terraform_remote_state.schemes_database.outputs.name
  database_username          = data.terraform_remote_state.schemes_database.outputs.username
  database_password          = data.terraform_remote_state.schemes_database.outputs.password
  oidc_server_metadata_url   = data.terraform_remote_state.identity.outputs.oidc_server_metadata_url
  resource_server_identifier = data.terraform_remote_state.identity.outputs.resource_server_identifier
  keep_idle                  = local.config[local.env].keep_idle
  docs_auth                  = local.config[local.env].docs_auth
  monitoring                 = local.config[local.env].monitoring
  domain                     = local.config[local.env].domain

  depends_on = [
    google_project_service.run,
    google_project_service.secret_manager,
    google_project_service.sql_admin
  ]
}

module "web_application_firewall" {
  source = "./web-application-firewall"
}

module "load_balancer" {
  source                 = "./load-balancer"
  region                 = var.location
  domain                 = local.config[local.env].domain
  cloud_run_service_name = module.application.name
  security_policy_id     = module.web_application_firewall.security_policy_id
}

module "github_action_deploy" {
  count = local.config[local.env].github_action_deploy ? 1 : 0

  source                       = "./github-action-deploy"
  project                      = local.project
  docker_repository_project    = data.terraform_remote_state.docker_repository.outputs.project
  cloud_run_service_account_id = module.application.service_account_id
}
