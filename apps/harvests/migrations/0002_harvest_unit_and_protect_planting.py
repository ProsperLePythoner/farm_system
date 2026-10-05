import decimal

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


def copy_crop_units_to_harvests(apps, schema_editor):
    Harvest = apps.get_model("harvests", "Harvest")
    for harvest in Harvest.objects.select_related("planting__crop").iterator():
        harvest.unit = harvest.planting.crop.unit
        harvest.save(update_fields=["unit"])


class Migration(migrations.Migration):
    dependencies = [
        ("crops", "0001_initial"),
        ("harvests", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="harvest",
            name="unit",
            field=models.CharField(default="", max_length=20),
            preserve_default=False,
        ),
        migrations.RunPython(
            copy_crop_units_to_harvests,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="harvest",
            name="planting",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="harvests",
                to="crops.planting",
            ),
        ),
        migrations.AlterField(
            model_name="harvest",
            name="quantity_harvested",
            field=models.DecimalField(
                decimal_places=2,
                max_digits=12,
                validators=[
                    django.core.validators.MinValueValidator(decimal.Decimal("0.01"))
                ],
            ),
        ),
        migrations.AlterModelOptions(
            name="harvest",
            options={"ordering": ["-harvesting_date", "-pk"]},
        ),
    ]
