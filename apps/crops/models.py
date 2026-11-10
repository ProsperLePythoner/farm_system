"""Production catalogue models and the calculated planting harvest window."""

from datetime import timedelta
from django.core.validators import MinValueValidator

from django.db import models
from django.utils import timezone
from django.db.models import DateField, DurationField, ExpressionWrapper, F
from django.db.models.functions import Cast

# Length of the harvest window after its first day (three calendar days in
# total, inclusive). Shared by Planting.harvest_end and the SQL version below
# so the two can never disagree.
HARVEST_WINDOW_EXTRA_DAYS = 2

class Field(models.Model):
    """
    Physical farm block.

    Examples:
    - Block A
    - Greenhouse 1
    - Plot C

    The stored field size is measured in acres.
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

    The maturity period and output unit support planting and harvest records.
    """

    class Unit(models.TextChoices):
        GRAM = "g", "Gram (g)"
        KILOGRAM = "kg", "Kilogram (kg)"
        TONNE = "tonne", "Tonne"
        BAG = "bag", "Bag"
        CRATE = "crate", "Crate"
        BUNCH = "bunch", "Bunch"
        HEADS = "heads", "Heads"
        PIECES = "pcs", "Pieces (pcs)"

    crop_name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Specific name for crop",
    )

    maturity_days = models.PositiveIntegerField(
        verbose_name="Maturity period in days",
    )

    unit = models.CharField(
        max_length=20,
        choices=Unit.choices,
        verbose_name="Harvest and sales unit",
    )

    description = models.TextField(
        blank=True
    )

    def __str__(self):
        return self.crop_name

class PlantingQuerySet(models.QuerySet):
    """Planting queries that can calculate harvest windows inside the database."""

    def with_harvest_window(self):
        """Annotate ``window_start`` and ``window_end`` (dates).

        These equal ``Planting.harvest_start`` and ``Planting.harvest_end`` but
        are computed by the database, so a page can ask for "windows that end
        today or later" without loading every planting ever recorded into
        Python and filtering there.
        """
        one_day = timedelta(days=1)
        start = Cast(
            F("planting_date")
            + ExpressionWrapper(F("crop__maturity_days") * one_day, output_field=DurationField()),
            DateField(),
        )
        return self.annotate(window_start=start).annotate(
            window_end=Cast(
                F("window_start") + timedelta(days=HARVEST_WINDOW_EXTRA_DAYS),
                DateField(),
            )
        )

class Planting(models.Model):
    """
    Represents a planting event.

    Example:

    Tomatoes planted in Block A
    on 1 January 2026. (lol, the dev's birthday 🙂)

    Expected harvest dates are calculated from the crop's maturity period.
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

    objects = PlantingQuerySet.as_manager()

    # ------------------------------
    # Computed Properties
    # ------------------------------

    @property
    def harvest_start(self):
        """
        First expected harvest day.

        Calculated dynamically.
        Not stored in database.
        Specifically, this is planting_date plus the crop's maturity_days.
        """
        return (
            self.planting_date
            + timedelta(days=self.crop.maturity_days)
        )

    @property
    def harvest_end(self):
        """
        Last day of a three-calendar-day harvest window, including harvest_start.

        The inclusive window ends at harvest_start plus two days.
        """
        return self.harvest_start + timedelta(days=HARVEST_WINDOW_EXTRA_DAYS)

    @property
    def is_ready_for_harvest(self):
        """
        Returns True if crop should
        already be harvestable.
        """
        # localdate(), not now().date(): the latter is the UTC date and would
        # flip to "ready" a few hours early or late for a farm in another zone.
        return timezone.localdate() >= self.harvest_start

    @property
    def status(self):
        """Return the planting's current state from its harvest window and records."""
        today = timezone.localdate()
        has_harvests = self.harvests.exists()

        if today > self.harvest_end:
            return "done" if has_harvests else "missed"
        if has_harvests and today >= self.harvest_start:
            return "partial"
        if not has_harvests and today >= self.harvest_start:
            return "ready"

        days_until_start = (self.harvest_start - today).days
        if not has_harvests and 0 < days_until_start <= 7:
            return "soon"
        return "growing"

    def __str__(self):
        return f"{self.crop.crop_name} - {self.field.field_name}"