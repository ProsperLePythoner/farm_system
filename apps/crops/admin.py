# crops/admin.py

from django.contrib import admin
from .models import Field, Crop, Planting

admin.site.register(Field)
admin.site.register(Crop)
admin.site.register(Planting)