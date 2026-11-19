
import os
import subprocess
import sys

from dotenv import dotenv_values
from urllib.parse import urlparse

production_env = dotenv_values(".env.production.local")
database_url = production_env.get("DATABASE_URL")

if not database_url:
    raise SystemExit("ERROR: DATABASE_URL was not found.")

host = urlparse(database_url).hostname

if not host or not host.endswith(".neon.tech"):
    raise SystemExit("ERROR: This is not a recognised Neon database host.")

env = os.environ.copy()
env["DATABASE_URL"] = database_url

command = [
    sys.executable,
    "manage.py",
    "setup_roles",
]

print("Target database:", host)
print("Running production role synchronization...")

subprocess.run(command, env=env, check=True)
