from .roles import ROLE_NAMES


def account_role(request):
    role_display = ""
    if request.user.is_authenticated:
        role_display = (
            request.user.groups.filter(name__in=ROLE_NAMES)
            .order_by("name")
            .values_list("name", flat=True)
            .first()
            or ("Superuser" if request.user.is_superuser else "")
        )
    return {"account_role_display": role_display}
