from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand, CommandError

from apps.accounts.roles import ROLE_PERMISSIONS


class Command(BaseCommand):
    help = "Create or update the standard farm-management role groups."

    def handle(self, *args, **options):
        requested = {
            permission
            for permissions in ROLE_PERMISSIONS.values()
            for permission in permissions
        }
        permissions_by_name = {
            f"{permission.content_type.app_label}.{permission.codename}": permission
            for permission in Permission.objects.select_related("content_type")
            if f"{permission.content_type.app_label}.{permission.codename}" in requested
        }
        missing = sorted(requested - permissions_by_name.keys())
        if missing:
            raise CommandError(
                "Required model permissions are missing; apply migrations first: "
                + ", ".join(missing)
            )

        for role_name, permission_names in ROLE_PERMISSIONS.items():
            group, created = Group.objects.get_or_create(name=role_name)
            group.permissions.set(
                permissions_by_name[name] for name in permission_names
            )
            state = "Created" if created else "Updated"
            self.stdout.write(f"{state} {role_name}")
