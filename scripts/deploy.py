"""Deploy the same immutable image to migrations and API; preserve existing secrets."""

import json
import os
import secrets
import subprocess
import sys

import yaml

image = os.environ.get("IMAGE", "demo-devops:local")
overlay = sys.argv[1] if len(sys.argv) > 1 else "k8s/base"


def run(*args, data=None, capture=False):
    return subprocess.run(args, input=data, text=True, check=True, capture_output=capture)


def apply(documents):
    run("kubectl", "apply", "-f", "-", data=yaml.safe_dump_all(documents))


manifest = run("kubectl", "kustomize", overlay, capture=True).stdout
docs = list(yaml.safe_load_all(manifest))
apply([d for d in docs if d["kind"] == "Namespace"])
existing = subprocess.run(
    ["kubectl", "-n", "devsu", "get", "secret", "demo-secret", "--ignore-not-found", "-o", "name"],
    check=True,
    capture_output=True,
    text=True,
)
if not existing.stdout.strip():
    password = os.environ.get("POSTGRES_PASSWORD") or secrets.token_hex(24)
    key = os.environ.get("DJANGO_SECRET_KEY") or secrets.token_urlsafe(48)
    apply(
        [
            {
                "apiVersion": "v1",
                "kind": "Secret",
                "metadata": {"name": "demo-secret", "namespace": "devsu"},
                "type": "Opaque",
                "stringData": {
                    "DJANGO_SECRET_KEY": key,
                    "POSTGRES_PASSWORD": password,
                    "DATABASE_URL": f"postgres://devsu:{password}@postgres:5432/devsu",
                },
            }
        ]
    )
prereq = {"Namespace", "ConfigMap", "Service", "StatefulSet"}
apply([d for d in docs if d["kind"] in prereq and d["kind"] != "Namespace"])
run("kubectl", "-n", "devsu", "rollout", "status", "statefulset/postgres", "--timeout=300s")
with open("k8s/migrate.yaml") as file:
    migration = yaml.safe_load(file)
migration["spec"]["template"]["spec"]["containers"][0]["image"] = image
run("kubectl", "-n", "devsu", "delete", "job", "demo-migrate", "--ignore-not-found", "--wait=true")
apply([migration])
run(
    "kubectl",
    "-n",
    "devsu",
    "wait",
    "--for=condition=complete",
    "job/demo-migrate",
    "--timeout=200s",
)
for doc in docs:
    if doc["kind"] == "Deployment":
        doc["spec"]["template"]["spec"]["containers"][0]["image"] = image
        # HPA owns replicas after the first deploy; avoid resetting its desired count.
        current = run(
            "kubectl",
            "-n",
            "devsu",
            "get",
            "deployment",
            "demo-api",
            "--ignore-not-found",
            "-o",
            "json",
            capture=True,
        ).stdout
        if current.strip():
            doc["spec"]["replicas"] = json.loads(current)["spec"]["replicas"]
apply([d for d in docs if d["kind"] not in prereq])
run("kubectl", "-n", "devsu", "rollout", "status", "deployment/demo-api", "--timeout=300s")
print("Deployment ready:", image)
