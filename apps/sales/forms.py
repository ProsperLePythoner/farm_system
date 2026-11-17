"""Forms and inline formset validation for orders and their line items."""

from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory
from django.utils import timezone

from apps.harvests.models import Harvest
from .models import Order, OrderItem, Payment


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["customer", "order_date", "notes"]
        widgets = {
            "order_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 4}),
        }


class OrderItemForm(forms.ModelForm):
    """Select a harvest for each new sale line and capture quantity and price."""

    harvest = forms.ModelChoiceField(
        queryset=Harvest.objects.none(),
        required=False,
        help_text="New sale items must be linked to a specific harvest.",
    )

    class Meta:
        model = OrderItem
        fields = ["harvest", "quantity", "unit_price"]
        labels = {
            "unit_price": "Unit price",
        }
        help_texts = {
            "unit_price": (
                "Price for one unit of the selected harvest produce. "
                "Quantity multiplied by unit price gives the line total."
            ),
        }

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
    """Require an order to keep at least one non-deleted item."""

    def add_fields(self, form, index):
        """Explain that selecting DELETE removes this row when the order is saved."""
        super().add_fields(form, index)
        if "DELETE" in form.fields:
            form.fields["DELETE"].label = "Remove this item"
            form.fields["DELETE"].help_text = "Removed when you save the order."

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


class PaymentForm(forms.ModelForm):
    """Record one payment installment against a single order.

    The order comes from the URL, not from the form, so a payment cannot be
    attached to a different order by editing the submitted data. A payment may
    not exceed what the customer still owes, which keeps the outstanding
    balance from silently going negative.
    """

    class Meta:
        model = Payment
        fields = ["amount_paid", "payment_date"]
        labels = {
            "amount_paid": "Amount received (TSh)",
            "payment_date": "Date received",
        }
        widgets = {
            "payment_date": forms.DateInput(attrs={"type": "date"}),
            "amount_paid": forms.NumberInput(attrs={"step": "0.01", "min": "0.01", "inputmode": "decimal"}),
        }

    def __init__(self, *args, order, **kwargs):
        super().__init__(*args, **kwargs)
        self.order = order
        self.fields["payment_date"].initial = timezone.localdate()
        self.fields["amount_paid"].help_text = (
            f"Outstanding balance: TSh {order.outstanding_balance:,.2f}."
        )

    def clean_amount_paid(self):
        amount = self.cleaned_data["amount_paid"]
        balance = self.order.outstanding_balance
        if amount > balance:
            raise forms.ValidationError(
                f"This is more than the outstanding balance of TSh {balance:,.2f}."
            )
        return amount

    def clean_payment_date(self):
        payment_date = self.cleaned_data["payment_date"]
        if payment_date > timezone.localdate():
            raise forms.ValidationError("The payment date cannot be in the future.")
        return payment_date
