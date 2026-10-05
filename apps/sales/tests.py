from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError
from django.test import TestCase
from django.urls import reverse

from apps.crops.models import Crop, Field, Planting
from apps.customers.models import Customer
from apps.harvests.models import Harvest

from .models import Order, OrderItem, Payment


class SalesOrderWorkflowTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            customer_name="Mlimani Market",
            customer_phone="+255 700 123456",
        )
        self.field = Field.objects.create(
            field_name="North plot",
            field_size=Decimal("1.00"),
        )
        self.tomatoes = Crop.objects.create(
            crop_name="Tomatoes",
            maturity_days=60,
            unit="kg",
        )
        self.onions = Crop.objects.create(
            crop_name="Onions",
            maturity_days=90,
            unit="kg",
        )
        self.tomato_harvest = self.make_harvest(
            self.tomatoes, Decimal("200.00"), date(2026, 10, 1)
        )
        self.onion_harvest = self.make_harvest(
            self.onions, Decimal("100.00"), date(2026, 10, 2)
        )

    def make_harvest(self, crop, quantity, harvested_on):
        planting = Planting.objects.create(
            crop=crop,
            field=self.field,
            planting_qty_unit="seeds",
            quantity_planted=Decimal("20.00"),
            planting_date=date(2026, 1, 1),
        )
        return Harvest.objects.create(
            planting=planting,
            harvesting_date=harvested_on,
            quantity_harvested=quantity,
            unit=crop.unit,
        )

    def order_form_data(self):
        return {
            "customer": str(self.customer.pk),
            "order_date": "2026-10-05",
            "notes": "",
            "items-TOTAL_FORMS": "2",
            "items-INITIAL_FORMS": "0",
            "items-MIN_NUM_FORMS": "0",
            "items-MAX_NUM_FORMS": "1000",
            "items-0-harvest": str(self.tomato_harvest.pk),
            "items-0-quantity": "50.00",
            "items-0-unit_price": "2000.00",
            "items-1-harvest": str(self.onion_harvest.pk),
            "items-1-quantity": "20.00",
            "items-1-unit_price": "1500.00",
        }

    def test_order_list_displays_orders_and_create_action(self):
        order = self.make_order_with_item()

        response = self.client.get(reverse("sales:order-list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mlimani Market")
        self.assertContains(response, "TSh 100000.00")
        self.assertContains(
            response,
            reverse("sales:order-detail", args=[order.pk]),
        )
        self.assertContains(response, reverse("sales:order-create"))

    def test_order_create_saves_order_and_harvest_linked_items(self):
        response = self.client.post(
            reverse("sales:order-create"),
            self.order_form_data(),
        )

        order = Order.objects.get()
        self.assertRedirects(
            response,
            reverse("sales:order-detail", args=[order.pk]),
        )
        items = list(order.items.select_related("crop", "harvest").order_by("pk"))
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].crop, self.tomatoes)
        self.assertEqual(items[0].harvest, self.tomato_harvest)
        self.assertEqual(items[0].unit, "kg")
        self.assertEqual(items[0].line_total, Decimal("100000.00"))
        self.assertEqual(items[1].line_total, Decimal("30000.00"))
        self.assertEqual(order.total_amount, Decimal("130000.00"))

    def test_order_creation_shows_one_success_message(self):
        response = self.client.post(
            reverse("sales:order-create"),
            self.order_form_data(),
            follow=True,
        )

        self.assertContains(response, "Order created.")
        self.assertEqual(response.content.count(b"Order created."), 1)

    def test_order_create_requires_harvest_for_new_line_items(self):
        data = self.order_form_data()
        data.update({
            "items-TOTAL_FORMS": "1",
            "items-1-harvest": "",
            "items-1-quantity": "",
            "items-1-unit_price": "",
            "items-0-harvest": "",
        })

        response = self.client.post(reverse("sales:order-create"), data)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Order.objects.exists())
        self.assertContains(response, "Select a harvest for this sale item.")

    def test_order_create_requires_at_least_one_item(self):
        data = self.order_form_data()
        data.update({
            "items-TOTAL_FORMS": "1",
            "items-0-harvest": "",
            "items-0-quantity": "",
            "items-0-unit_price": "",
        })

        response = self.client.post(reverse("sales:order-create"), data)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Order.objects.exists())
        self.assertContains(response, "An order must contain at least one item.")

    def test_order_detail_shows_totals_and_harvest_source(self):
        order = self.make_order_with_item()
        Payment.objects.create(
            order=order,
            amount_paid=Decimal("80000.00"),
            payment_date=date(2026, 10, 5),
        )

        response = self.client.get(reverse("sales:order-detail", args=[order.pk]))

        self.assertContains(response, "Tomatoes")
        self.assertContains(response, "North plot")
        self.assertContains(response, "TSh 100000.00")
        self.assertContains(response, "TSh 80000.00")
        self.assertContains(response, "TSh 20000.00")

    def test_order_can_be_updated_without_losing_existing_line(self):
        order = self.make_order_with_item()
        response = self.client.post(
            reverse("sales:order-update", args=[order.pk]),
            {
                "customer": str(self.customer.pk),
                "order_date": "2026-10-06",
                "notes": "Updated",
                "items-TOTAL_FORMS": "2",
                "items-INITIAL_FORMS": "1",
                "items-MIN_NUM_FORMS": "0",
                "items-MAX_NUM_FORMS": "1000",
                f"items-0-id": str(order.items.get().pk),
                "items-0-harvest": str(self.tomato_harvest.pk),
                "items-0-quantity": "45.00",
                "items-0-unit_price": "2000.00",
                "items-1-harvest": "",
                "items-1-quantity": "",
                "items-1-unit_price": "",
            },
        )

        self.assertRedirects(response, reverse("sales:order-detail", args=[order.pk]))
        order.refresh_from_db()
        item = order.items.get()
        self.assertEqual(order.order_date, date(2026, 10, 6))
        self.assertEqual(item.quantity, Decimal("45.00"))
        self.assertEqual(item.harvest, self.tomato_harvest)

    def test_legacy_crop_only_items_remain_readable(self):
        order = Order.objects.create(
            customer=self.customer,
            order_date=date(2026, 10, 5),
        )
        OrderItem.objects.create(
            order=order,
            crop=self.tomatoes,
            quantity=Decimal("3.00"),
            unit_price=Decimal("2000.00"),
            unit="kg",
        )

        response = self.client.get(reverse("sales:order-detail", args=[order.pk]))

        self.assertContains(response, "Legacy crop-only item")
        self.assertContains(response, "3.00 kg")

    def test_harvest_cannot_be_deleted_once_referenced_by_sale(self):
        self.make_order_with_item()

        with self.assertRaises(ProtectedError):
            self.tomato_harvest.delete()

    def test_order_cannot_be_deleted_when_it_has_payment_history(self):
        order = self.make_order_with_item()
        Payment.objects.create(
            order=order,
            amount_paid=Decimal("10.00"),
            payment_date=date(2026, 10, 5),
        )

        response = self.client.post(
            reverse("sales:order-delete", args=[order.pk])
        )

        self.assertEqual(response.status_code, 409)
        self.assertContains(response, "payment history", status_code=409)
        self.assertTrue(Order.objects.filter(pk=order.pk).exists())

    def test_order_without_payment_history_can_be_deleted(self):
        order = self.make_order_with_item()

        response = self.client.post(
            reverse("sales:order-delete", args=[order.pk])
        )

        self.assertRedirects(response, reverse("sales:order-list"))
        self.assertFalse(Order.objects.filter(pk=order.pk).exists())

    def test_order_item_rejects_harvest_for_another_crop(self):
        item = OrderItem(
            order=Order(customer=self.customer, order_date=date(2026, 10, 5)),
            crop=self.onions,
            harvest=self.tomato_harvest,
            quantity=Decimal("1.00"),
            unit_price=Decimal("1.00"),
            unit="kg",
        )

        with self.assertRaises(ValidationError):
            item.full_clean()

    def make_order_with_item(self):
        order = Order.objects.create(
            customer=self.customer,
            order_date=date(2026, 10, 5),
        )
        OrderItem.objects.create(
            order=order,
            crop=self.tomatoes,
            harvest=self.tomato_harvest,
            quantity=Decimal("50.00"),
            unit_price=Decimal("2000.00"),
            unit="kg",
        )
        return order
