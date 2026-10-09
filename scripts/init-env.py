"""Generate local credentials without overwriting an existing .env."""

import secrets
from pathlib import Path

path = Path(__file__).resolve().parent.parent / ".env"
with path.open("x") as file:
    file.write(f"DJANGO_SECRET_KEY={secrets.token_urlsafe(48)}\n")
    file.write("DJANGO_DEBUG=False\nDJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,demo.local\n")
    file.write("POSTGRES_DB=devsu\nPOSTGRES_USER=devsu\n")
    file.write(f"POSTGRES_PASSWORD={secrets.token_hex(24)}\n")
path.chmod(0o600)
print("Created .env with random local credentials.")
