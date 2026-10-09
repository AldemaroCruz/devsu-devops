# Validation performed — 2026-10-09

These are actual checks performed during authoring, not a GitHub Actions execution.
Raw local results are in `docs/evidence/local/`.

| Check | Result |
| --- | --- |
| Django test suite on SQLite, Python 3.12 | 12 tests passed |
| Coverage of measured API runtime code | 100% (40 statements); excludes tests/migrations/framework registration |
| Ruff lint and formatting | Passed |
| Bandit on API and Django modules | No findings |
| pip-audit of pinned runtime requirements | No known vulnerabilities reported by its database |
| Django system checks and migration drift | Passed; no pending model changes |
| collectstatic and database migrations | Passed |
| Gunicorn HTTP smoke with SQLite | Live/ready, create/get/list/delete passed |
| Static asset via Gunicorn/WhiteNoise | HTTP 200 |
| Workflow syntax with actionlint 1.7.7 | Passed |
| Kustomize base and GKE overlay rendering | Passed using kubectl 1.34.0 |
| Kubernetes schemas with kubeconform 0.7.0 | 19 resources valid against Kubernetes 1.34.0; no skips/errors |
| Terraform 1.13.3 formatting | Passed |
| Terraform provider initialization | Passed; google 7.46.1 lock file generated |
| Terraform validate | Blocked by host restrictions: provider cannot open its Unix socket |
| Docker build/Compose/image scan | Pending; Docker is not installed in authoring environment |
| PostgreSQL tests and actual Kubernetes rollout | Pending in GitHub Actions or candidate environment |
| GCP plan/apply and public endpoint | Not performed; no cloud resources created |

Terraform provider startup fails here with `listen unix ... socket: operation not permitted`.
This is a host limitation, not a successful schema validation. The workflow includes real
`terraform validate` on a normal GitHub runner and will block the image build if validation fails.

Action references were resolved from their official GitHub tag references and pinned to commit SHAs.
The Traefik chart version was checked against its published chart index.
The first pipeline run remains necessary to validate integration and to produce submission evidence.

Primary references consulted:
- [Django 5.2.18 security release](https://www.djangoproject.com/weblog/2026/oct/06/security-releases/)
- [Community ingress-nginx retirement](https://kubernetes.io/blog/2026/01/29/ingress-nginx-statement/)
- [Traefik Kubernetes setup](https://doc.traefik.io/traefik/setup/kubernetes/)
- [GCP federation for deployment pipelines](https://docs.cloud.google.com/iam/docs/workload-identity-federation-with-deployment-pipelines)
- [GKE ingress health checks](https://docs.cloud.google.com/kubernetes-engine/docs/concepts/ingress-routing-security)
