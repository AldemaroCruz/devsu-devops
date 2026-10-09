terraform {
  required_version = ">= 1.6, < 2.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 8.5"
    }
  }
  # Configure a dedicated GCS backend before use with a team.
  # Local state is ignored by git; protect it as sensitive material.
}
provider "google" {
  project = var.project_id
  region  = var.region
}
