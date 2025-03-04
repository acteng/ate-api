terraform {
  backend "gcs" {
    bucket = "dft-ate-api-common-tf-backend"
    prefix = "service"
  }
}

locals {
  env     = terraform.workspace
  project = "${var.project_prefix}-${local.env}"
}

data "terraform_remote_state" "docker_repository" {
  backend = "gcs"
  config = {
    bucket = "${var.project_prefix}-common-tf-backend"
    prefix = "docker-repository"
  }
}

resource "google_project_service" "run" {
  project = local.project
  service = "run.googleapis.com"
}

module "application" {
  source                    = "./application"
  project                   = local.project
  region                    = var.location
  docker_repository_project = data.terraform_remote_state.docker_repository.outputs.project
  docker_repository_url     = data.terraform_remote_state.docker_repository.outputs.url

  depends_on = [google_project_service.run]
}
