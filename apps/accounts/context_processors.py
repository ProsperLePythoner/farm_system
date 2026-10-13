"""Template context values shared by pages that render account identity."""

from .roles import ROLE_NAMES


def account_role(request):
    """Expose one recognized group name for the shared navigation bar."""
    role_display = ""
    user = getattr(request, "user", None)
    if user and user.is_authenticated:
        role_display = (
            user.groups.filter(name__in=ROLE_NAMES)
            .order_by("name")
            .values_list("name", flat=True)
            .first()
            or ("Superuser" if user.is_superuser else "")
        )
    return {"account_role_display": role_display}
