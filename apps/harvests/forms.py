from django import forms

from .models import Harvest


class HarvestForm(forms.ModelForm):
    class Meta:
        model = Harvest
        fields = ["harvesting_date", "quantity_harvested", "notes"]
        widgets = {
            "harvesting_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 4}),
        }
