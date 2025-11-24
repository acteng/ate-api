variable "name" {
  description = "OAuth client name"
  type        = string
}

variable "env" {
  description = "App environment"
  type        = string
}

variable "description" {
  description = "OAuth client description"
  type        = string
}

variable "owner" {
  description = "OAuth client owner object ID"
  type        = string
}

variable "audience" {
  description = "Resource server identifier to grant client access to"
  type        = string
}

# variable "app_role_id" {
#   description = "Resource server app role ID to grant client access to"
#   type        = string
# }

variable "service_principal_id" {
  description = "Resource server service principal object ID to grant client access to"
  type        = string
}
