# harvests/admin.py

from django.contrib import admin

from .models import Harvest


@admin.register(Harvest)
class HarvestAdmin(admin.ModelAdmin):
    list_display = ("planting", "harvesting_date", "quantity_harvested", "unit")
    list_filter = ("harvesting_date", "planting__crop")
    search_fields = ("planting__crop__crop_name", "planting__field__field_name")
    raw_id_fields = ("planting",)
    readonly_fields = ("unit",)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.unit = obj.planting.crop.unit
        super().save_model(request, obj, form, change)