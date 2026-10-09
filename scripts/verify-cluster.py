"""Check two ready pods share PostgreSQL and HPA receives CPU metrics."""

import json
import subprocess
import time
import uuid


def kubectl(*args):
    return subprocess.check_output(["kubectl", "-n", "devsu", *args], text=True)


pods = json.loads(kubectl("get", "pods", "-l", "app=demo-api", "-o", "json"))["items"]
ready = [
    p["metadata"]["name"]
    for p in pods
    if any(
        c["type"] == "Ready" and c["status"] == "True" for c in p["status"].get("conditions", [])
    )
]
assert len(ready) >= 2, ready
payload = {"name": "Cross Pod Test", "dni": uuid.uuid4().hex[:13]}
create = (
    "import json,urllib.request; "
    f"data=json.dumps({payload!r}).encode(); "
    "r=urllib.request.Request('http://localhost:8000/api/users/',data=data,"
    "headers={'Content-Type':'application/json'},method='POST'); "
    "print(urllib.request.urlopen(r).read().decode())"
)
user = json.loads(kubectl("exec", ready[0], "--", "python", "-c", create))
try:
    read = (
        "import urllib.request; "
        f"print(urllib.request.urlopen('http://localhost:8000/api/users/{user['id']}/').read().decode())"
    )
    assert json.loads(kubectl("exec", ready[1], "--", "python", "-c", read)) == user
finally:
    delete = (
        "import urllib.request; "
        f"r=urllib.request.Request('http://localhost:8000/api/users/{user['id']}/',method='DELETE'); "
        "print(urllib.request.urlopen(r).status)"
    )
    assert kubectl("exec", ready[0], "--", "python", "-c", delete).strip() == "204"
for attempt in range(30):
    hpa = json.loads(kubectl("get", "hpa", "demo-api", "-o", "json"))
    if hpa.get("status", {}).get("currentMetrics"):
        break
    time.sleep(5)
else:
    raise RuntimeError("HPA has no CPU metrics")
print("PASS: two ready API pods, cross-pod persistence, HPA metrics available")
