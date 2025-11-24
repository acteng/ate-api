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

variable "user_pool_id" {
  description = "User pool the client belongs to"
  type        = string
}

variable "scopes" {
  description = "OAuth scopes allowed for this client"
  type        = list(string)
}
