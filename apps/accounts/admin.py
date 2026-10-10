from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group

from .roles import ROLE_ADMINISTRATOR

User = get_user_model()

admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    def has_add_permission(self, request):
        return request.user.is_superuser and super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        if (
            obj is not None
            and not request.user.is_superuser
            and (
                obj.is_superuser
                or obj.groups.filter(name=ROLE_ADMINISTRATOR).exists()
            )
        ):
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return False

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        protected_fields = {"password"}
        if not request.user.is_superuser:
            protected_fields.update(
                {"groups", "user_permissions", "is_staff", "is_superuser"}
            )
        if obj is not None and obj.pk == request.user.pk:
            protected_fields.add("is_active")
        return tuple(
            (
                title,
                {
                    **options,
                    "fields": tuple(
                        field
                        for field in options["fields"]
                        if field not in protected_fields
                    ),
                },
            )
            for title, options in fieldsets
            if any(
                field not in protected_fields
                for field in options["fields"]
            )
        )


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
