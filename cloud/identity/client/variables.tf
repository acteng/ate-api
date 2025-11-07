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
