from django import forms
from .models import Crop, Field, Planting


class CropForm(forms.ModelForm):
    class Meta:
        model = Crop
        fields = ["crop_name", "maturity_days", "unit", "description"]
        labels = {
            "crop_name": "Crop name",
            "maturity_days": "Maturity period (days)",
            "unit": "Harvest and sales unit",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }


class FieldForm(forms.ModelForm):
    class Meta:
        model = Field
        fields = ["field_name", "field_size", "notes"]
        labels = {
            "field_name": "Field, plot, or block name",
            "field_size": "Size (acres)",
        }
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 4}),
        }


class PlantingForm(forms.ModelForm):
    class Meta:
        model = Planting
        fields = [
            "crop",
            "field",
            "planting_qty_unit",
            "quantity_planted",
            "planting_date",
            "notes",
        ]

        widgets = {
            "planting_date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "rows": 4,
                }
            ),
        }