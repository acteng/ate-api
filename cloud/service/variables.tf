variable "project_prefix" {
  description = "GCP project prefix"
  type        = string
  default     = "dft-ate-api"
}

variable "database_project_prefix" {
  description = "Database GCP project prefix"
  type        = string
  default     = "dft-ate-capitalschemes"
}

variable "location" {
  description = "GCP location"
  type        = string
  default     = "europe-west1"
}
