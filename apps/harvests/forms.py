"""Form for recording or editing a harvest's date, quantity, and notes."""

from django import forms

from .models import Harvest


class HarvestForm(forms.ModelForm):
    class Meta:
        model = Harvest
        fields = ["harvesting_date", "quantity_harvested", "notes"]
        labels = {
            "quantity_harvested": "Quantity harvested",
        }
        help_texts = {
            "quantity_harvested": (
                "Enter harvested output in the crop's harvest unit. "
                "The planting quantity may use a different unit."
            ),
        }
        widgets = {
            "harvesting_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 4}),
        }
