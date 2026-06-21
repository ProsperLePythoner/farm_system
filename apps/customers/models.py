from django.db import models


class Customer(models.Model):
    """
    Person or business
    buying produce.
    """

    customer_name = models.CharField(
        max_length=255
    )

    customer_phone = models.CharField(
        max_length=50
    )

    customer_location = models.CharField(
        max_length=255,
        blank=True
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Description or notes-to-self about " \
        "the customer, e.g. stingy/mbahili, or maybe stubborn? 🙂"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.customer_name