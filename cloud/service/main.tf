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
  env                      = terraform.workspace
  project                  = "${var.project_prefix}-${local.env}"
  database_project         = "${var.database_project_prefix}-${local.env}"
  database_connection_name = "${local.database_project}:europe-west1:dft-ate-capital-schemes"
}

data "terraform_remote_state" "docker_repository" {
  backend = "gcs"
  config = {
    bucket = "${var.project_prefix}-common-tf-backend"
    prefix = "docker-repository"
  }
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
  database_project           = local.database_project
  database_connection_name   = local.database_connection_name
  database_url_secret_id     = "database-url"
  oidc_server_metadata_url   = data.terraform_remote_state.identity.outputs.oidc_server_metadata_url
  resource_server_identifier = data.terraform_remote_state.identity.outputs.resource_server_identifier

  depends_on = [google_project_service.run]
}

module "github_action_deploy" {
  source                       = "./github-action-deploy"
  project                      = local.project
  docker_repository_project    = data.terraform_remote_state.docker_repository.outputs.project
  cloud_run_service_account_id = module.application.service_account_id
}
