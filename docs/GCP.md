# Optional GCP deployment

## Prerequisites and cost

Use a dedicated Google Cloud project with billing enabled, Terraform >=1.6 and gcloud.
The applying identity needs permissions for service enablement, networking, GKE, Artifact Registry,
service accounts, IAM policy changes and Workload Identity Federation. These are bootstrap
permissions, separate from the much narrower pipeline deployer. Organization policy may restrict
public GKE control planes, resource locations or external load balancers; adapt to your project.

Autopilot, persistent disk and an external HTTP load balancer incur charges. This package does not
configure a budget or promise a fixed cost. Review pricing and your project budget before applying.

## Bootstrap from Cloud Shell

Get the immutable numeric GitHub repository ID from the public GitHub API:
`https://api.github.com/repos/OWNER/REPOSITORY` (field `id`). Keep the exact repository-name case.

```bash
gcloud config set project YOUR-DEDICATED-PROJECT
cd infra/gcp
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars.
terraform init
terraform fmt -check
terraform validate
terraform plan -out=demo.tfplan
terraform apply demo.tfplan
terraform output
```

Cloud Shell already supplies gcloud user authentication; on a standalone workstation use
`gcloud auth application-default login`. For team use, bootstrap a dedicated protected GCS
state bucket and configure a backend; do not commit state or a plan.

Terraform creates a custom VPC/subnet, Autopilot cluster, node service account, regional registry,
deployer service account and GitHub OIDC federation. OIDC acceptance is restricted to the exact
repository, numeric repository ID, `main`, and this workflow path. The GitHub job requires
`id-token: write`; it impersonates the deployer without a long-lived key.

The node identity has `roles/container.defaultNodeServiceAccount` and registry-reader access.
The deployer has `roles/container.developer` in the dedicated project and writer access to the
single registry. Secret creation and namespace creation therefore work for this demo. Restrict
namespace access with RBAC and pre-provision these objects for a production installation.

## Actions setup

Create the `gke-demo` GitHub environment, restrict deployments to `main`, and copy these
repository Actions variables from `terraform output github_variables`:

| Variable | Meaning |
| --- | --- |
| GCP_PROJECT_ID | Dedicated project |
| GCP_REGION | us-east1 by default |
| GKE_CLUSTER | devsu-demo |
| GCP_WIF_PROVIDER | Full provider resource name |
| GCP_DEPLOY_SA | Deployer service-account email |
| ENABLE_GKE_CD | Set to `true` only after provisioning is complete |

Rerun the workflow on main. The GKE job imports the exact previously tested image artifact,
pushes it to Artifact Registry and deploys its digest. The GKE controller handles the Ingress;
do not install the local metrics-server override in GKE. Autopilot provides resource metrics.

The migration Job is executed before updating API pods. Database migrations must be backward
compatible with the previous application version during a rolling deployment. A rollback of
Deployment does not reverse a schema change.

## Endpoint and evidence

```bash
gcloud container clusters get-credentials devsu-demo --region us-east1 --project YOUR-PROJECT
kubectl -n devsu get ingress demo-api -w
kubectl -n devsu get pods,hpa,pvc
```

The public ingress IP may take several minutes to become available. Then run:
`python scripts/smoke.py http://PUBLIC_IP`.
The GKE pipeline initially verifies the Service through port-forward; public ingress readiness
and public endpoint access are separate evidence tasks. The demo endpoint is HTTP and unauthenticated;
TLS/DNS must be configured before any production use. No real personal information is needed.

Save sanitized Terraform apply/output logs and the real Actions run URL in `docs/EVIDENCE.md`.
Do not publish `.tfstate`, `.tfplan`, the generated secret, credential files or access tokens.

## Cleanup

First set `ENABLE_GKE_CD=false` to prevent a new pipeline from redeploying.
Export anything you need; the commands below delete the demo and its database data:

```bash
kubectl delete namespace devsu --wait=true
cd infra/gcp
terraform plan -destroy -out=destroy.tfplan
terraform apply destroy.tfplan
```

Deleting Kubernetes ingress before the cluster lets the controller clean up the load balancer.
Verify no forwarding rules/disks remain in the dedicated project. APIs remain enabled by design.
