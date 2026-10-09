output "github_variables" {
  value = {
    GCP_PROJECT_ID   = var.project_id
    GCP_REGION       = var.region
    GKE_CLUSTER      = google_container_cluster.demo.name
    GCP_WIF_PROVIDER = google_iam_workload_identity_pool_provider.github.name
    GCP_DEPLOY_SA    = google_service_account.deploy.email
  }
}
output "registry" {
  value = "${var.region}-docker.pkg.dev/${var.project_id}/devsu/demo"
}
