from django.db import models
from django.core.validators import MinValueValidator


class Harvest(models.Model):
    """
    A single harvest event.

    One planting can produce
    many harvest records.
    """

    planting = models.ForeignKey(
        "crops.Planting",
        on_delete=models.CASCADE, # Delete a planting, all harvest records go swoosh... bye-bye!
        related_name="harvests"
    )

    harvesting_date = models.DateField()

    '''
    Corrected from:
    
        harvest_unit = models.CharField(
        max_length=20,
        verbose_name="Physical unit for measuring harvest for"
                    f" {planting.crop.crop_name}"
        )
    
    To THIS (below)... to avoid duplicate data'''

    # --------------------------
    # Computed property
    # --------------------------
    
    @property
    def unit(self):
        return self.planting.crop.unit

    quantity_harvested = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)] # validate input (positive only)
    )

    notes = models.TextField(
        blank=True
    )

    def __str__(self):
        return (
            f"{self.planting.crop.crop_name} " # remove space?
            f" ({self.quantity_harvested}{self.unit})"
        )
