from datetime import date
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from apps.harvests.models import Harvest
from apps.sales.models import Order, OrderItem
from apps.customers.models import Customer

from .forms import CropForm
from .models import Crop, Field, Planting


class CropAndFieldWorkflowTests(TestCase):
    def setUp(self):
        self.crop = Crop.objects.create(
            crop_name="Tomatoes",
            maturity_days=60,
            unit=Crop.Unit.KILOGRAM,
        )
        self.field = Field.objects.create(
            field_name="North plot",
            field_size=Decimal("1.25"),
        )
        self.planting = Planting.objects.create(
            crop=self.crop,
            field=self.field,
            planting_qty_unit="seeds",
            quantity_planted=Decimal("40.00"),
            planting_date=date(2026, 10, 1),
        )

    def test_crop_list_and_detail_show_crop_and_plantings(self):
        response = self.client.get(reverse("crops:crop-list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tomatoes")
        self.assertContains(response, reverse("crops:crop-create"))

        detail = self.client.get(reverse("crops:crop-detail", args=[self.crop.pk]))
        self.assertContains(detail, "North plot")
        self.assertContains(
            detail,
            reverse("crops:planting-detail", args=[self.planting.pk]),
        )

    def test_crop_can_be_created_and_updated(self):
        response = self.client.post(
            reverse("crops:crop-create"),
            {
                "crop_name": "Onions",
                "maturity_days": "90",
                "unit": Crop.Unit.BAG,
                "description": "",
            },
        )

        self.assertRedirects(response, reverse("crops:crop-list"))
        onions = Crop.objects.get(crop_name="Onions")
        self.assertEqual(onions.unit, Crop.Unit.BAG)

        response = self.client.post(
            reverse("crops:crop-update", args=[onions.pk]),
            {
                "crop_name": "Red onions",
                "maturity_days": "95",
                "unit": Crop.Unit.BAG,
                "description": "Updated",
            },
        )
        self.assertRedirects(response, reverse("crops:crop-list"))
        onions.refresh_from_db()
        self.assertEqual(onions.crop_name, "Red onions")
        self.assertEqual(onions.maturity_days, 95)

    def test_success_message_is_rendered_after_creating_crop(self):
        response = self.client.post(
            reverse("crops:crop-create"),
            {
                "crop_name": "Peppers",
                "maturity_days": "70",
                "unit": Crop.Unit.KILOGRAM,
                "description": "",
            },
            follow=True,
        )

        self.assertContains(response, "Crop created.")
    def test_crop_form_rejects_unknown_measurement_unit(self):
        form = CropForm(data={
            "crop_name": "Unknown",
            "maturity_days": 50,
            "unit": "some-unit",
            "description": "",
        })

        self.assertFalse(form.is_valid())
        self.assertIn("unit", form.errors)

    def test_crop_delete_is_explained_and_blocked_when_used_by_planting(self):
        response = self.client.get(reverse("crops:crop-delete", args=[self.crop.pk]))
        self.assertContains(response, "cannot be deleted")
        self.assertNotContains(response, "Yes, delete crop")

        response = self.client.post(reverse("crops:crop-delete", args=[self.crop.pk]))
        self.assertEqual(response.status_code, 409)
        self.assertTrue(Crop.objects.filter(pk=self.crop.pk).exists())

    def test_crop_delete_is_blocked_when_used_by_legacy_order_item(self):
        customer = Customer.objects.create(
            customer_name="Market",
            customer_phone="123",
        )
        order = Order.objects.create(customer=customer, order_date=date(2026, 10, 5))
        OrderItem.objects.create(
            order=order,
            crop=self.crop,
            quantity=Decimal("1.00"),
            unit_price=Decimal("10.00"),
            unit="kg",
        )

        response = self.client.post(reverse("crops:crop-delete", args=[self.crop.pk]))

        self.assertEqual(response.status_code, 409)
        self.assertTrue(Crop.objects.filter(pk=self.crop.pk).exists())

    def test_field_list_and_detail_show_plantings(self):
        response = self.client.get(reverse("crops:field-list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "North plot")
        detail = self.client.get(reverse("crops:field-detail", args=[self.field.pk]))
        self.assertContains(detail, "Tomatoes")
        self.assertContains(
            detail,
            reverse("crops:planting-detail", args=[self.planting.pk]),
        )

    def test_field_can_be_created_and_updated(self):
        response = self.client.post(
            reverse("crops:field-create"),
            {
                "field_name": "Greenhouse",
                "field_size": "0.50",
                "notes": "",
            },
        )

        self.assertRedirects(response, reverse("crops:field-list"))
        greenhouse = Field.objects.get(field_name="Greenhouse")

        response = self.client.post(
            reverse("crops:field-update", args=[greenhouse.pk]),
            {
                "field_name": "Greenhouse 1",
                "field_size": "0.75",
                "notes": "Covered",
            },
        )
        self.assertRedirects(response, reverse("crops:field-list"))
        greenhouse.refresh_from_db()
        self.assertEqual(greenhouse.field_name, "Greenhouse 1")
        self.assertEqual(greenhouse.field_size, Decimal("0.75"))

    def test_field_delete_is_blocked_when_it_has_plantings(self):
        response = self.client.post(reverse("crops:field-delete", args=[self.field.pk]))

        self.assertEqual(response.status_code, 409)
        self.assertTrue(Field.objects.filter(pk=self.field.pk).exists())

    def test_unreferenced_crop_and_field_can_be_deleted(self):
        crop = Crop.objects.create(
            crop_name="Corn",
            maturity_days=75,
            unit=Crop.Unit.PIECES,
        )
        field = Field.objects.create(
            field_name="East plot",
            field_size=Decimal("2.00"),
        )

        self.assertRedirects(
            self.client.post(reverse("crops:crop-delete", args=[crop.pk])),
            reverse("crops:crop-list"),
        )
        self.assertRedirects(
            self.client.post(reverse("crops:field-delete", args=[field.pk])),
            reverse("crops:field-list"),
        )
        self.assertFalse(Crop.objects.filter(pk=crop.pk).exists())
        self.assertFalse(Field.objects.filter(pk=field.pk).exists())

    def test_planting_form_links_to_create_missing_catalogue_entries(self):
        self.planting.delete()
        Crop.objects.all().delete()
        Field.objects.all().delete()

        response = self.client.get(reverse("crops:planting-create"))

        self.assertContains(response, reverse("crops:crop-create"))
        self.assertContains(response, reverse("crops:field-create"))
        self.assertContains(response, "Add a crop before creating your first planting.")

    def test_crop_overview_shows_catalogue_counts(self):
        response = self.client.get(reverse("crops:overview"))

        self.assertContains(response, "1 crops")
        self.assertContains(response, "1 fields")
        self.assertContains(response, "1 plantings")

    def test_delete_planting_with_harvest_renders_blocked_state(self):
        Harvest.objects.create(
            planting=self.planting,
            harvesting_date=date(2026, 12, 1),
            quantity_harvested=Decimal("5.00"),
            unit="kg",
        )

        response = self.client.post(
            reverse("crops:planting-delete", args=[self.planting.pk])
        )

        self.assertEqual(response.status_code, 409)
        self.assertTrue(Planting.objects.filter(pk=self.planting.pk).exists())
