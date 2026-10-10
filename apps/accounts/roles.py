ROLE_ADMINISTRATOR = "Administrator"
ROLE_FARM_MANAGER = "Farm Manager"
ROLE_HARVEST_MANAGER = "Harvest Manager"
ROLE_SALES_MANAGER = "Sales Manager"
ROLE_STAFF = "Staff"

ROLE_NAMES = (
    ROLE_ADMINISTRATOR,
    ROLE_FARM_MANAGER,
    ROLE_HARVEST_MANAGER,
    ROLE_SALES_MANAGER,
    ROLE_STAFF,
)

OPERATIONAL_MODELS = {
    "crops": ("crop", "field", "planting"),
    "harvests": ("harvest",),
    "customers": ("customer",),
    "sales": ("order", "orderitem", "payment"),
}


def model_permissions(app_label, model_names, actions):
    return tuple(
        f"{app_label}.{action}_{model_name}"
        for model_name in model_names
        for action in actions
    )


ALL_OPERATIONAL_PERMISSIONS = tuple(
    permission
    for app_label, model_names in OPERATIONAL_MODELS.items()
    for permission in model_permissions(
        app_label,
        model_names,
        ("view", "add", "change", "delete"),
    )
)
READ_OPERATIONAL_PERMISSIONS = tuple(
    permission
    for app_label, model_names in OPERATIONAL_MODELS.items()
    for permission in model_permissions(app_label, model_names, ("view",))
)

ROLE_PERMISSIONS = {
    ROLE_ADMINISTRATOR: ALL_OPERATIONAL_PERMISSIONS + (
        "auth.view_user",
        "auth.add_user",
        "auth.change_user",
    ),
    ROLE_FARM_MANAGER: ALL_OPERATIONAL_PERMISSIONS,
    ROLE_HARVEST_MANAGER: (
        *model_permissions("crops", ("crop", "field", "planting"), ("view",)),
        "harvests.view_harvest",
        "harvests.add_harvest",
        "harvests.change_harvest",
    ),
    ROLE_SALES_MANAGER: (
        *model_permissions("crops", ("crop", "field", "planting"), ("view",)),
        "harvests.view_harvest",
        *model_permissions("customers", ("customer",), ("view", "add", "change")),
        *model_permissions("sales", ("order", "orderitem"), ("view", "add", "change")),
        *model_permissions("sales", ("payment",), ("view", "add", "change")),
    ),
    ROLE_STAFF: tuple(
        permission
        for permission in READ_OPERATIONAL_PERMISSIONS
        if permission != "sales.view_payment"
    ),
}
