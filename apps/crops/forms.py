from django import forms
from .models import Planting


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