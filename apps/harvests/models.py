"""Harvest event model and validation for a planting's recorded output."""

from django.db import models
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator


class Harvest(models.Model):
    """
    A single harvest event.

    One planting can produce
    many harvest records.

    Each record retains the unit used when that harvest was recorded.
    """

    planting = models.ForeignKey(
        "crops.Planting",
        on_delete=models.PROTECT,
        related_name="harvests",
    )

    harvesting_date = models.DateField()

    unit = models.CharField(max_length=20)

    quantity_harvested = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-harvesting_date", "-pk"]

    def clean(self):
        """Reject a harvest date that precedes its associated planting."""
        super().clean()
        if (
            self.planting_id
            and self.harvesting_date
            and self.harvesting_date < self.planting.planting_date
        ):
            raise ValidationError({
                "harvesting_date": "Harvest date cannot be before the planting date."
            })

    def __str__(self):
        return (
            f"{self.planting.crop.crop_name} "
            f"({self.quantity_harvested} {self.unit}) on {self.harvesting_date}"
        )
