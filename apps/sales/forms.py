from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory

from apps.harvests.models import Harvest

from .models import Order, OrderItem


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["customer", "order_date", "notes"]
        widgets = {
            "order_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 4}),
        }


class OrderItemForm(forms.ModelForm):
    harvest = forms.ModelChoiceField(
        queryset=Harvest.objects.none(),
        required=False,
        help_text="New sale items must be linked to a specific harvest.",
    )

    class Meta:
        model = OrderItem
        fields = ["harvest", "quantity", "unit_price"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["harvest"].queryset = (
            Harvest.objects
            .select_related("planting__crop", "planting__field")
            .order_by("-harvesting_date", "-pk")
        )

    def clean(self):
        cleaned_data = super().clean()
        harvest = cleaned_data.get("harvest")
        quantity = cleaned_data.get("quantity")
        unit_price = cleaned_data.get("unit_price")

        if not self.instance.pk and (quantity or unit_price) and not harvest:
            self.add_error("harvest", "Select a harvest for this sale item.")

        return cleaned_data

    def save(self, commit=True):
        item = super().save(commit=False)
        if item.harvest_id:
            item.crop = item.harvest.planting.crop
            item.unit = item.harvest.unit
        if commit:
            item.save()
            self.save_m2m()
        return item


class BaseOrderItemFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return

        remaining_items = 0
        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get("DELETE"):
                continue
            if form.instance.pk or form.cleaned_data.get("harvest"):
                remaining_items += 1

        if remaining_items == 0:
            raise forms.ValidationError("An order must contain at least one item.")


OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    formset=BaseOrderItemFormSet,
    fields=["harvest", "quantity", "unit_price"],
    extra=1,
    can_delete=True,
)
