from django.contrib import admin

from .models import Field, Crop, Planting


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ("field_name", "field_size")
    search_fields = ("field_name",)


@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ("crop_name", "maturity_days", "unit")
    search_fields = ("crop_name",)


@admin.register(Planting)
class PlantingAdmin(admin.ModelAdmin):
    list_display = ("crop", "field", "planting_date", "quantity_planted")
    list_select_related = ("crop", "field")
    list_filter = ("crop", "field")