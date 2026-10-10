from django.contrib.auth.mixins import UserPassesTestMixin

from .roles import ROLE_ADMINISTRATOR, ROLE_NAMES


def has_application_role(user):
    return user.is_authenticated and (
        user.is_superuser
        or user.groups.filter(name__in=ROLE_NAMES).exists()
    )


def is_account_administrator(user):
    return user.is_authenticated and (
        user.is_superuser
        or user.groups.filter(name=ROLE_ADMINISTRATOR).exists()
    )


class AccountAdministratorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return is_account_administrator(self.request.user)


class ApplicationRoleRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return has_application_role(self.request.user)
