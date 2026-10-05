import django.db.models.deletion
from django.db import migrations, models


def copy_crop_units_to_order_items(apps, schema_editor):
    OrderItem = apps.get_model("sales", "OrderItem")
    for item in OrderItem.objects.select_related("crop").iterator():
        item.unit = item.crop.unit
        item.save(update_fields=["unit"])


class Migration(migrations.Migration):
    dependencies = [
        ("harvests", "0002_harvest_unit_and_protect_planting"),
        ("sales", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="orderitem",
            name="harvest",
            field=models.ForeignKey(
                blank=True,
                help_text="Blank only for sales entered before harvest tracking.",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="order_items",
                to="harvests.harvest",
            ),
        ),
        migrations.AddField(
            model_name="orderitem",
            name="unit",
            field=models.CharField(default="", max_length=20),
            preserve_default=False,
        ),
        migrations.RunPython(
            copy_crop_units_to_order_items,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="orderitem",
            name="crop",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="order_items",
                to="crops.crop",
            ),
        ),
        migrations.AlterField(
            model_name="payment",
            name="order",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="payments",
                to="sales.order",
            ),
        ),
    ]
