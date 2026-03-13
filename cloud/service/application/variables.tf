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

variable "database_name" {
  description = "Database name"
  type        = string
}

variable "database_username" {
  description = "Database username"
  type        = string
}

variable "database_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "oidc_server_metadata_url" {
  description = "Authorisation server configuration endpoint"
  type        = string
}

variable "resource_server_identifier" {
  description = "Resource server identifier"
  type        = string
}

variable "keep_idle" {
  description = "Whether to keep an instance idle to prevent cold starts"
  type        = bool
}

variable "monitoring" {
  description = "Whether to enable monitoring"
  type        = bool
}

variable "domain" {
  description = "Domain name to monitor"
  type        = string
}
