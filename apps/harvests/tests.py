from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import date_format

from apps.crops.models import Crop, Field, Planting

from .forms import HarvestForm
from .models import Harvest


class HarvestTests(TestCase):
    def setUp(self):
        admin = get_user_model().objects.create_superuser(
            username="workflow-admin",
            email="admin@example.test",
            password="test-password",
        )
        self.client.force_login(admin)
        self.crop = Crop.objects.create(
            crop_name="Tomatoes",
            maturity_days=60,
            unit="kg",
        )
        self.field = Field.objects.create(
            field_name="North plot",
            field_size=Decimal("1.00"),
        )
        self.planting = Planting.objects.create(
            crop=self.crop,
            field=self.field,
            planting_qty_unit="seeds",
            quantity_planted=Decimal("20.00"),
            planting_date=date(2026, 1, 1),
        )

    def test_form_rejects_harvest_before_planting(self):
        form = HarvestForm(
            data={
                "harvesting_date": "2025-12-31",
                "quantity_harvested": "5.00",
                "notes": "",
            },
            instance=Harvest(planting=self.planting),
        )

        self.assertFalse(form.is_valid())
        self.assertIn("harvesting_date", form.errors)

    def test_quantity_must_be_positive(self):
        harvest = Harvest(
            planting=self.planting,
            harvesting_date=date(2026, 2, 1),
            quantity_harvested=Decimal("0.00"),
            unit=self.crop.unit,
        )

        with self.assertRaises(ValidationError):
            harvest.full_clean()

    def test_create_view_sets_planting_and_snapshots_unit(self):
        response = self.client.post(
            reverse("harvests:harvest-create", args=[self.planting.pk]),
            {
                "harvesting_date": "2026-02-01",
                "quantity_harvested": "5.00",
                "notes": "",
            },
        )

        self.assertRedirects(
            response,
            reverse("crops:planting-detail", args=[self.planting.pk]),
        )
        harvest = Harvest.objects.get()
        self.assertEqual(harvest.planting, self.planting)
        self.assertEqual(harvest.unit, "kg")

    def test_list_view_shows_harvest_records(self):
        Harvest.objects.create(
            planting=self.planting,
            harvesting_date=date(2026, 2, 1),
            quantity_harvested=Decimal("5.00"),
            unit="kg",
        )

        response = self.client.get(reverse("harvests:harvest-list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "5.00 kg")
        self.assertContains(response, "North plot")

    def test_list_view_shows_upcoming_window_and_record_action(self):
        planting = Planting.objects.create(
            crop=self.crop,
            field=self.field,
            planting_qty_unit="seeds",
            quantity_planted=Decimal("20.00"),
            planting_date=timezone.localdate(),
        )

        response = self.client.get(reverse("harvests:harvest-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["upcoming_plantings"]), [planting])
        self.assertEqual(list(response.context["harvests"]), [])
        self.assertContains(response, "Upcoming Harvest Windows")
        self.assertContains(response, date_format(planting.harvest_start, "DATE_FORMAT"))
        self.assertContains(
            response,
            reverse("harvests:harvest-create", args=[planting.pk]),
        )
        self.assertContains(response, "Record Harvest")

    def test_list_view_includes_a_window_that_is_open_today(self):
        planting = Planting.objects.create(
            crop=self.crop,
            field=self.field,
            planting_qty_unit="seeds",
            quantity_planted=Decimal("20.00"),
            planting_date=timezone.localdate() - timedelta(days=62),
        )

        response = self.client.get(reverse("harvests:harvest-list"))

        self.assertEqual(list(response.context["upcoming_plantings"]), [planting])

    def test_complete_upcoming_planting_to_harvest_lifecycle(self):
        planting = Planting.objects.create(
            crop=self.crop,
            field=self.field,
            planting_qty_unit="seeds",
            quantity_planted=Decimal("20.00"),
            planting_date=timezone.localdate(),
        )
        harvest_list_url = reverse("harvests:harvest-list")

        upcoming_response = self.client.get(harvest_list_url)
        self.assertContains(
            upcoming_response,
            date_format(planting.harvest_start, "DATE_FORMAT"),
        )
        self.assertContains(
            upcoming_response,
            reverse("harvests:harvest-create", args=[planting.pk]),
        )

        create_response = self.client.post(
            reverse("harvests:harvest-create", args=[planting.pk]),
            {
                "harvesting_date": planting.harvest_start.isoformat(),
                "quantity_harvested": "5.00",
                "notes": "First picking",
            },
        )
        self.assertRedirects(
            create_response,
            reverse("crops:planting-detail", args=[planting.pk]),
        )

        harvest = Harvest.objects.get(planting=planting)
        record_response = self.client.get(harvest_list_url)
        self.assertEqual(list(record_response.context["harvests"]), [harvest])
        self.assertContains(record_response, "5.00 kg")
        self.assertContains(record_response, "First picking")

    def test_update_preserves_the_recorded_unit(self):
        harvest = Harvest.objects.create(
            planting=self.planting,
            harvesting_date=date(2026, 2, 1),
            quantity_harvested=Decimal("5.00"),
            unit="kg",
        )
        self.crop.unit = "crates"
        self.crop.save(update_fields=["unit"])

        response = self.client.post(
            reverse("harvests:harvest-update", args=[harvest.pk]),
            {
                "harvesting_date": "2026-02-02",
                "quantity_harvested": "6.00",
                "notes": "",
            },
        )

        self.assertRedirects(
            response,
            reverse("crops:planting-detail", args=[self.planting.pk]),
        )
        harvest.refresh_from_db()
        self.assertEqual(harvest.unit, "kg")
        self.assertEqual(harvest.quantity_harvested, Decimal("6.00"))

    def test_delete_view_returns_to_planting_detail(self):
        harvest = Harvest.objects.create(
            planting=self.planting,
            harvesting_date=date(2026, 2, 1),
            quantity_harvested=Decimal("5.00"),
            unit="kg",
        )

        response = self.client.post(
            reverse("harvests:harvest-delete", args=[harvest.pk])
        )

        self.assertRedirects(
            response,
            reverse("crops:planting-detail", args=[self.planting.pk]),
        )
        self.assertFalse(Harvest.objects.filter(pk=harvest.pk).exists())

    def test_harvest_delete_is_blocked_when_referenced_by_an_order(self):
        from apps.customers.models import Customer
        from apps.sales.models import Order, OrderItem

        harvest = Harvest.objects.create(
            planting=self.planting,
            harvesting_date=date(2026, 2, 1),
            quantity_harvested=Decimal("5.00"),
            unit="kg",
        )
        customer = Customer.objects.create(
            customer_name="Market",
            customer_phone="123",
        )
        order = Order.objects.create(customer=customer, order_date=date(2026, 2, 2))
        OrderItem.objects.create(
            order=order,
            crop=self.crop,
            harvest=harvest,
            quantity=Decimal("1.00"),
            unit_price=Decimal("10.00"),
            unit="kg",
        )

        response = self.client.post(
            reverse("harvests:harvest-delete", args=[harvest.pk])
        )

        self.assertEqual(response.status_code, 409)
        self.assertContains(response, "referenced by a sale", status_code=409)
        self.assertTrue(Harvest.objects.filter(pk=harvest.pk).exists())

    def test_planting_cannot_be_deleted_while_harvests_exist(self):
        Harvest.objects.create(
            planting=self.planting,
            harvesting_date=date(2026, 2, 1),
            quantity_harvested=Decimal("5.00"),
            unit="kg",
        )

        with self.assertRaises(ProtectedError):
            self.planting.delete()
