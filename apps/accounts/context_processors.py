"""Template context values shared by pages that render account identity."""

from .permissions import get_role_names


def account_role(request):
    """Expose one recognized group name for the shared navigation bar."""
    role_display = ""
    user = getattr(request, "user", None)
    if user and user.is_authenticated:
        # Shares the per-request role lookup with the permission mixins.
        role_names = sorted(get_role_names(user))
        role_display = (
            role_names[0] if role_names
            else ("Superuser" if user.is_superuser else "")
        )
    return {"account_role_display": role_display}
