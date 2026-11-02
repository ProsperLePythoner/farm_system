"""Sales models for customer orders, line items, and payment installments."""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import DecimalField, ExpressionWrapper, F, OuterRef, Subquery, Sum, Value
from django.db.models.functions import Coalesce

class OrderQuerySet(models.QuerySet):
    """Order queries that can compute money totals inside the database."""

    def with_totals(self):
        """Annotate ``annotated_total``, ``annotated_paid`` and ``annotated_balance``.

        The totals are summed by the database in one query, instead of loading
        every item and payment row of every order into Python. Two correlated
        sub-queries are used on purpose: joining items and payments in a single
        query would repeat each payment once per item and inflate the sums.

        ``Order.total_amount``, ``total_paid`` and ``outstanding_balance``
        transparently use these values when present, so templates do not change.
        """
        items = (
            OrderItem.objects.filter(order=OuterRef("pk"))
            .order_by()
            .values("order")
            .annotate(
                total=Sum(
                    ExpressionWrapper(F("quantity") * F("unit_price"), output_field=MONEY)
                )
            )
            .values("total")
        )
        payments = (
            Payment.objects.filter(order=OuterRef("pk"))
            .order_by()
            .values("order")
            .annotate(total=Sum("amount_paid"))
            .values("total")
        )
        zero = Value(0, output_field=MONEY)
        return self.annotate(
            annotated_total=Coalesce(Subquery(items, output_field=MONEY), zero),
            annotated_paid=Coalesce(Subquery(payments, output_field=MONEY), zero),
        ).annotate(annotated_balance=F("annotated_total") - F("annotated_paid"))

    def with_outstanding_balance(self):
        """Orders whose recorded payments do not yet cover their total."""
        return self.with_totals().filter(annotated_balance__gt=0)

MONEY = DecimalField(max_digits=16, decimal_places=2)


class Order(models.Model):
    """
    Customer purchase.

    Totals are derived from related order items and payments.
    """

    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.PROTECT,
        related_name="orders"
    )

    order_date = models.DateField()

    notes = models.TextField(
        blank=True
    )

    # ------------------------------
    # TIMESTAMP FIELDS!

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    # ------------------------------

    objects = OrderQuerySet.as_manager()

    @property
    def total_amount(self):
        """
        Sum of all order items.

        Not stored.
        Calculated. 🐱‍👤 (Cat-stealthy smart)

        Each order item's quantity multiplied by its unit price contributes.
        When the order came from ``Order.objects.with_totals()`` the database
        has already summed it, so no extra rows are read.
        """

        if hasattr(self, "annotated_total"):
            return self.annotated_total

        total = Decimal("0.00")

        for item in self.items.all():
            total += item.line_total

        return total # i.e., derived value

    @property
    def total_paid(self):
        """Sum of recorded payment installments."""
        if hasattr(self, "annotated_paid"):
            return self.annotated_paid
        return sum(
            (payment.amount_paid for payment in self.payments.all()),
            Decimal("0.00"),
        )

    @property
    def outstanding_balance(self):
        '''
        Determine the order's outstanding balance (payment due)

        The value is calculated as the order total minus recorded payments.
        '''

        if hasattr(self, "annotated_balance"):
            return self.annotated_balance
        return self.total_amount - self.total_paid
    
    @property
    def status(self):
        '''
        Determine the status of the order's payment

        (probably useful for some arbitrary dashboard)
        '''

        total_paid = self.total_paid
        if total_paid == 0:
            return "pending"

        if total_paid < self.total_amount:
            return "partial"

        return "paid"

    # ------------------------------

    '''
    Not urgent, but eventually add model validation:
    
    def clean(self):
    if self.amount_paid > self.order.outstanding_balance:
        raise ValidationError(...)
    '''

    def __str__(self):
        return f"{self.customer.customer_name} [{self.order_date}]"


class OrderItem(models.Model):
    """
    Single line item
    inside an order.

    A new item can link the sold quantity to a specific harvest.
    """

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    crop = models.ForeignKey(
        "crops.Crop",
        on_delete=models.PROTECT,
        related_name="order_items",
    )

    harvest = models.ForeignKey(
        "harvests.Harvest",
        on_delete=models.PROTECT,
        related_name="order_items",
        null=True,
        blank=True,
        help_text="Blank only for sales entered before harvest tracking.",
    )

    unit = models.CharField(max_length=20)

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))]
    )

    @property
    def line_total(self):
        """Calculate quantity multiplied by the item's unit price."""
        return self.quantity * self.unit_price

    def clean(self):
        """Require a selected harvest to belong to the selected crop."""
        super().clean()
        if self.harvest_id and self.crop_id:
            harvest_crop_id = self.harvest.planting.crop_id
            if self.crop_id != harvest_crop_id:
                raise ValidationError({
                    "harvest": "The selected harvest must be for the selected crop."
                })

    def save(self, *args, **kwargs):
        """Copy crop and unit from a linked harvest for historical consistency."""
        if self.harvest_id:
            self.crop = self.harvest.planting.crop
            self.unit = self.harvest.unit
        elif not self.unit and self.crop_id:
            self.unit = self.crop.unit
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.crop.crop_name} - {self.quantity}"


class Payment(models.Model):
    """
    Payment installment.

    Multiple installments may contribute to an order's total paid.
    """

    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="payments",
    )

    amount_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))]
    )

    @property
    def payment_due(self):
        """Placeholder; outstanding balance is currently calculated on Order."""
        pass # implement this to calculate outstanding balance dynamically

    payment_date = models.DateField()

    # ------------------------------
    # TIMESTAMP FIELDS!

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    # ------------------------------


    def __str__(self):
        return (
            f"Payment received: Tsh.{self.amount_paid}, for {self.order}"
        )