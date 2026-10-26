"""Reusable checks for recognized application roles and administrators."""

from django.contrib.auth.mixins import UserPassesTestMixin

from .roles import ROLE_ADMINISTRATOR, ROLE_NAMES


def get_role_names(user):
    """Return the recognized role names held by ``user`` as a frozenset.

    The result is remembered on the user object, which Django creates once per
    request. The navigation bar and the permission mixins both need the role;
    before this helper each queried the database separately, and every query is
    a network round trip to the hosted database.

    The cache lives only as long as the user object. Code that changes a user's
    groups and then re-checks the *same* object must call
    ``clear_role_cache(user)`` first (Django's own permission cache behaves the
    same way).
    """
    if not user.is_authenticated:
        return frozenset()
    cached = getattr(user, "_application_role_names", None)
    if cached is None:
        cached = frozenset(
            user.groups.filter(name__in=ROLE_NAMES).values_list("name", flat=True)
        )
        user._application_role_names = cached
    return cached


def clear_role_cache(user):
    """Forget the remembered role names after a user's groups change."""
    if hasattr(user, "_application_role_names"):
        del user._application_role_names


def has_application_role(user):
    """Return whether an authenticated user has any app role or is a superuser."""
    return user.is_authenticated and (
        user.is_superuser or bool(get_role_names(user))
    )


def is_account_administrator(user):
    """Return whether an authenticated user can manage application accounts."""
    return user.is_authenticated and (
        user.is_superuser or ROLE_ADMINISTRATOR in get_role_names(user)
    )


class AccountAdministratorRequiredMixin(UserPassesTestMixin):
    """Deny a class-based view unless the requester is an account administrator."""

    def test_func(self):
        return is_account_administrator(self.request.user)


class ApplicationRoleRequiredMixin(UserPassesTestMixin):
    """Require a recognized role before the user can enter the dashboard."""

    def test_func(self):
        return has_application_role(self.request.user)
