"""HTTP smoke test; removes only the synthetic record it creates."""

import json
import sys
import uuid
from urllib.request import Request, urlopen

base = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:8000"
headers = {"Content-Type": "application/json", "Host": "demo.local"}


def call(path, method="GET", data=None):
    body = json.dumps(data).encode() if data is not None else None
    request = Request(base + path, data=body, headers=headers, method=method)
    with urlopen(request, timeout=10) as response:  # nosec B310: caller-controlled test URL
        content = response.read()
        return response.status, json.loads(content) if content else None


assert call("/health/live/")[0] == 200
assert call("/health/ready/")[0] == 200
status, user = call("/api/users/", "POST", {"name": "CI Smoke", "dni": uuid.uuid4().hex[:13]})
assert status == 201
try:
    assert call(f"/api/users/{user['id']}/")[1] == user
    assert user in call("/api/users/")[1]
finally:
    assert call(f"/api/users/{user['id']}/", "DELETE")[0] == 204
print("PASS: liveness, readiness, create, get, list, delete")
