from datetime import timedelta
from django.core.validators import MinValueValidator

from django.db import models
from django.utils import timezone


class Field(models.Model):
    """
    Physical farm block.

    Examples:
    - Block A
    - Greenhouse 1
    - Plot C
    """

    field_name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Name of field/plot/block"
    )

    field_size = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Field size in acres"
    )

    notes = models.TextField(
        blank=True
    )

    def __str__(self):
        return self.field_name


class Crop(models.Model):
    """
    Master crop definition.

    Examples:
    - Tomatoes
    - Sweet Corn
    - Capsicum
    """

    crop_name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Specific name for crop"
    )

    maturity_days = models.PositiveIntegerField()

    unit = models.CharField(
        max_length=20,
        verbose_name="Physical measurement unit"
    )

    description = models.TextField(
        blank=True
    )

    def __str__(self):
        return self.crop_name


class Planting(models.Model):
    """
    Represents a planting event.

    Example:

    Tomatoes planted in Block A
    on 1 January 2026. (lol, the dev's birthday 🙂)
    """

    crop = models.ForeignKey(
        Crop,
        on_delete=models.PROTECT,
        related_name="plantings"
    )

    field = models.ForeignKey(
        Field,
        on_delete=models.PROTECT,
        related_name="plantings"
    )

    planting_qty_unit = models.CharField(
        max_length=20,
        verbose_name="Planting quantity, e.g. seeds" \
        ", kg, etc."
    )

    quantity_planted = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    planting_date = models.DateField()

    notes = models.TextField(
        # User's personal notes on this exact planting
        blank=True,
    )

    # ------------------------------
    # Computed Properties
    # ------------------------------

    @property
    def harvest_start(self):
        """
        First expected harvest day.

        Calculated dynamically.
        Not stored in database.
        """
        return (
            self.planting_date
            + timedelta(days=self.crop.maturity_days)
        )

    @property
    def harvest_end(self):
        """
        Harvest window closes after 3 days.
        """
        return self.harvest_start + timedelta(days=3)

    @property
    def is_ready_for_harvest(self):
        """
        Returns True if crop should
        already be harvestable.
        """
        return timezone.now().date() >= self.harvest_start

    def __str__(self):
        return f"{self.crop.crop_name} - {self.field.field_name}"