locals {
  apis = toset([
    "compute.googleapis.com", "container.googleapis.com", "artifactregistry.googleapis.com",
    "iam.googleapis.com", "iamcredentials.googleapis.com", "sts.googleapis.com"
  ])
}
resource "google_project_service" "api" {
  for_each           = local.apis
  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}
data "google_project" "current" {
  project_id = var.project_id
}
resource "google_compute_network" "demo" {
  name                    = "devsu-demo"
  auto_create_subnetworks = false
  depends_on              = [google_project_service.api]
}
resource "google_compute_subnetwork" "demo" {
  name          = "devsu-demo"
  region        = var.region
  network       = google_compute_network.demo.id
  ip_cidr_range = "10.10.0.0/20"
  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = "10.20.0.0/16"
  }
  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = "10.30.0.0/20"
  }
}
resource "google_service_account" "nodes" {
  account_id   = "devsu-gke-nodes"
  display_name = "Devsu GKE node identity"
  depends_on   = [google_project_service.api]
}
resource "google_project_iam_member" "node_default" {
  project = var.project_id
  role    = "roles/container.defaultNodeServiceAccount"
  member  = "serviceAccount:${google_service_account.nodes.email}"
}
resource "google_container_cluster" "demo" {
  name                = "devsu-demo"
  location            = var.region
  enable_autopilot    = true
  deletion_protection = false
  network             = google_compute_network.demo.id
  subnetwork          = google_compute_subnetwork.demo.id
  release_channel {
    channel = "REGULAR"
  }
  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }
  cluster_autoscaling {
    auto_provisioning_defaults {
      service_account = google_service_account.nodes.email
    }
  }
  depends_on = [google_project_service.api, google_project_iam_member.node_default]
}
resource "google_artifact_registry_repository" "demo" {
  location      = var.region
  repository_id = "devsu"
  format        = "DOCKER"
  depends_on    = [google_project_service.api]
}
resource "google_artifact_registry_repository_iam_member" "nodes_pull" {
  location   = var.region
  repository = google_artifact_registry_repository.demo.name
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${google_service_account.nodes.email}"
}
resource "google_service_account" "deploy" {
  account_id   = "devsu-github-deploy"
  display_name = "GitHub Actions deployer"
  depends_on   = [google_project_service.api]
}
resource "google_project_iam_member" "deploy_gke" {
  project = var.project_id
  role    = "roles/container.developer"
  member  = "serviceAccount:${google_service_account.deploy.email}"
}
resource "google_artifact_registry_repository_iam_member" "deploy_push" {
  location   = var.region
  repository = google_artifact_registry_repository.demo.name
  role       = "roles/artifactregistry.writer"
  member     = "serviceAccount:${google_service_account.deploy.email}"
}
resource "google_iam_workload_identity_pool" "github" {
  workload_identity_pool_id = "devsu-github"
  display_name              = "Devsu GitHub OIDC"
  depends_on                = [google_project_service.api]
}
resource "google_iam_workload_identity_pool_provider" "github" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github.workload_identity_pool_id
  workload_identity_pool_provider_id = "github"
  attribute_mapping = {
    "google.subject"          = "assertion.sub"
    "attribute.repository"    = "assertion.repository"
    "attribute.repository_id" = "assertion.repository_id"
  }
  attribute_condition = "assertion.repository == '${var.github_repository}' && assertion.repository_id == '${var.github_repository_id}' && assertion.ref == 'refs/heads/main' && assertion.workflow_ref == '${var.github_repository}/.github/workflows/ci-cd.yaml@refs/heads/main'"
  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}
resource "google_service_account_iam_member" "github" {
  service_account_id = google_service_account.deploy.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/attribute.repository_id/${var.github_repository_id}"
}
