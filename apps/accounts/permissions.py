"""Reusable checks for recognized application roles and administrators."""

from django.contrib.auth.mixins import UserPassesTestMixin

from .roles import ROLE_ADMINISTRATOR, ROLE_NAMES


def has_application_role(user):
    """Return whether an authenticated user has any app role or is a superuser."""
    return user.is_authenticated and (
        user.is_superuser
        or user.groups.filter(name__in=ROLE_NAMES).exists()
    )


def is_account_administrator(user):
    """Return whether an authenticated user can manage application accounts."""
    return user.is_authenticated and (
        user.is_superuser
        or user.groups.filter(name=ROLE_ADMINISTRATOR).exists()
    )


class AccountAdministratorRequiredMixin(UserPassesTestMixin):
    """Deny a class-based view unless the requester is an account administrator."""

    def test_func(self):
        return is_account_administrator(self.request.user)


class ApplicationRoleRequiredMixin(UserPassesTestMixin):
    """Require a recognized role before the user can enter the dashboard."""

    def test_func(self):
        return has_application_role(self.request.user)
