from django import forms

from .models import Customer


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            "customer_name",
            "customer_phone",
            "customer_location",
            "notes",
        ]
        labels = {
            "customer_name": "Name",
            "customer_phone": "Phone",
            "customer_location": "Location",
            "notes": "Notes",
        }
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 4}),
        }
