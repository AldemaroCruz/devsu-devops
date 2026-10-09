variable "project_id" {
  type        = string
  description = "Dedicated demo project with billing already enabled."
}
variable "region" {
  type    = string
  default = "us-east1"
}
variable "github_repository" {
  type        = string
  description = "Exact owner/repository, case-sensitive in GitHub OIDC claims."
  validation {
    condition     = can(regex("^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$", var.github_repository))
    error_message = "Use owner/repository."
  }
}
variable "github_repository_id" {
  type        = string
  description = "Numeric immutable GitHub repository ID, protecting against name reuse."
  validation {
    condition     = can(regex("^[0-9]+$", var.github_repository_id))
    error_message = "Use the numeric repository ID."
  }
}
