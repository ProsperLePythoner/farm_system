from decimal import Decimal
from django.core.validators import MinValueValidator

from django.db import models
from django.db.models import Sum


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

        return total

    @property
    def total_paid(self):

        paid = self.payments.aggregate(
            total=Sum("amount_paid")
        )["total"]

        return paid or Decimal("0.00")

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

        if self.total_paid == 0:
            return "pending"

        if self.total_paid < self.total_amount:
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
        on_delete=models.PROTECT # Don't flush away orders upon deleting a crop
    )

    '''
    You don't really need to store this field
    because it's essentially duplicate data, but what the heck.
    Just keep it for now.'''
    # ---------------------------------

    #@property
    #def unit(self):
    #    return self.crop.unit
    # ---------------------------------
    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))] # Disallow zero values
    )

    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))]
    )

    @property
    def line_total(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.crop.crop_name} - {self.quantity}"


class Payment(models.Model):
    """
    Payment installment.
    """

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    amount_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))]
    )

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