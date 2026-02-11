variable "name" {
  description = "OAuth client name"
  type        = string
}

variable "description" {
  description = "OAuth client description"
  type        = string
}

variable "audience" {
  description = "Resource server identifier to grant client access to"
  type        = string
}

variable "public_key" {
  description = "Public key to verify client authentication signature in PEM format"
  type        = string
}
