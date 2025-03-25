variable "project" {
  description = "GCP project"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
}

variable "docker_repository_project" {
  description = "Docker repository GCP project"
  type        = string
}

variable "docker_repository_url" {
  description = "Docker repository URL"
  type        = string
}

variable "image_tag" {
  description = "Docker image tag"
  type        = string
}

variable "database_project" {
  description = "Database GCP project"
  type        = string
}

variable "database_connection_name" {
  description = "Database connection name"
  type        = string
}

variable "database_url_secret_id" {
  description = "Database URL secret ID"
  type        = string
}

variable "oidc_server_metadata_url" {
  description = "OIDC configuration URL"
  type        = string
}

variable "resource_server_identifier" {
  description = "Resource server identifier"
  type        = string
}
