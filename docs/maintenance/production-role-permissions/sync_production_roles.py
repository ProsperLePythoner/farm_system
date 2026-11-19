
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

from dotenv import dotenv_values

# Resolve project root (four levels above this file).
PROJECT_ROOT = Path(__file__).resolve().parents[3]

ENV_FILE = PROJECT_ROOT / ".env.production.local"
MANAGE_PY = PROJECT_ROOT / "manage.py"

database_url = dotenv_values(ENV_FILE).get("DATABASE_URL")

if not database_url:
    raise SystemExit("ERROR: Production DATABASE_URL is missing.")

host = urlparse(database_url).hostname

if not host or not host.endswith(".neon.tech"):
    raise SystemExit("ERROR: Unrecognised Neon database hostname.")

print(f"Production database: {host}")
print("This operation will synchronize Django role permissions.")

confirmation = input(
    "Type SYNC-PRODUCTION to continue: "
)

if confirmation != "SYNC-PRODUCTION":
    raise SystemExit("Synchronization cancelled.")

env = os.environ.copy()
env["DATABASE_URL"] = database_url

subprocess.run(
    [sys.executable, str(MANAGE_PY), "setup_roles"],
    cwd=PROJECT_ROOT,
    env=env,
    check=True,
)

print("Production role synchronization completed.")
