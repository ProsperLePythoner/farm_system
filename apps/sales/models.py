from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Order(models.Model):
    """
    Customer purchase.
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

    @property
    def total_amount(self):
        """
        Sum of all order items.

        Not stored.
        Calculated. 🐱‍👤 (Cat-stealthy smart)
        """

        total = Decimal("0.00")

        for item in self.items.all():
            total += item.line_total

        return total # i.e., derived value

    @property
    def total_paid(self):
        return sum(
            (payment.amount_paid for payment in self.payments.all()),
            Decimal("0.00"),
        )

    @property
    def outstanding_balance(self):
        '''
        Determine the order's outstanding balance (payment due)
        '''

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
        return self.quantity * self.unit_price

    def clean(self):
        super().clean()
        if self.harvest_id and self.crop_id:
            harvest_crop_id = self.harvest.planting.crop_id
            if self.crop_id != harvest_crop_id:
                raise ValidationError({
                    "harvest": "The selected harvest must be for the selected crop."
                })

    def save(self, *args, **kwargs):
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