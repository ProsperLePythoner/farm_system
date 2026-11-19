
from os import environ
import subprocess
import sys

from dotenv import dotenv_values

database_url = dotenv_values(".env.production.local").get("DATABASE_URL")

if not database_url:
    raise SystemExit("DATABASE_URL missing.")

env = environ.copy()
env["DATABASE_URL"] = database_url

code = """
from django.contrib.auth.models import Group

group = Group.objects.get(name="Farm Manager")

permissions = group.permissions.select_related("content_type")

user_permissions = permissions.filter(
    content_type__app_label="accounts",
    content_type__model="user",
)

print("User-management permissions:")

for permission in user_permissions:
    print(permission.codename)

if user_permissions.exists():
    print("WARNING: User-management permissions exist.")
else:
    print("PASS: No user-management permissions.")
"""

subprocess.run(
    [sys.executable, "manage.py", "shell", "-c", code],
    env=env,
    check=True,
)
