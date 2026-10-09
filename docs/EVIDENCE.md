# Submission evidence — fill with real execution results

## Current state

Local Python checks are recorded in `VALIDATION.md`. GitHub Actions, container execution and
Kubernetes rollout have **not** been executed by this package authoring session.
Replace the placeholders below only after running the corresponding operations.

| Deliverable | Actual link / file |
| --- | --- |
| Public GitHub repository | PENDING |
| Successful Actions run | PENDING |
| Public GHCR image and digest | PENDING |
| Quality and coverage artifact | PENDING |
| Trivy report | PENDING |
| Kubernetes resources and migration logs | PENDING |
| Ingress smoke and cross-pod persistence | PENDING |
| Optional public endpoint | PENDING / not deployed |
| Optional Terraform apply/output evidence | PENDING / not applied |

## Capture after Actions is green

Download `quality-reports`, `image-security-and-publication` and `kubernetes-evidence`.
Save them in `docs/evidence/`, copy the actual run/repository URLs above and commit the evidence.
Do not upload the large image tar file as submission evidence; the published image is in GHCR.
The automated cluster check validates two Ready API pods, shared records between distinct pods
and HPA CPU metrics. The ephemeral cluster is removed after each run.

## Optional scaling experiment

For stronger evidence, use your local cluster or GKE and watch:

```bash
kubectl -n devsu get hpa demo-api -w
kubectl -n devsu get pods -l app=demo-api -w
```

Generate bounded test traffic against `/api/users/` with a load generator, using synthetic data
only. Capture replicas rising above 2 and returning to the floor after the stabilization window.
Tune the concurrency for your hardware. Do not call mere HPA existence proof of actual scaling.

## Optional IaC extra points

Attach sanitized `terraform apply` and `terraform output` logs only after real execution.
Include provisioning and cleanup evidence. Terraform code alone does not satisfy the extra-point
request for deployment output.

## Rebuild the final ZIP

After adding evidence, use git's tracked files rather than packaging your working directory:

```bash
git add docs/evidence docs/EVIDENCE.md
git commit -m "Add assessment execution evidence"
git archive --format=zip --prefix=devsu-devops/ --output=../devsu-devops-final.zip HEAD
```
