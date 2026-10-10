from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.crops.models import Crop
from apps.sales.models import Order, OrderItem

from .forms import CustomerForm
from .models import Customer


class CustomerWorkflowTests(TestCase):
    def setUp(self):
        admin = get_user_model().objects.create_superuser(
            username="workflow-admin",
            email="admin@example.test",
            password="test-password",
        )
        self.client.force_login(admin)
        self.customer = Customer.objects.create(
            customer_name="Amina Market",
            customer_phone="+255 700 123456",
            customer_location="Arusha",
            notes="Weekly buyer",
        )

    def test_customer_list_shows_customer_and_actions(self):
        response = self.client.get(reverse("customers:customer-list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Amina Market")
        self.assertContains(
            response,
            reverse("customers:customer-detail", args=[self.customer.pk]),
        )
        self.assertContains(response, reverse("customers:customer-create"))

    def test_customer_can_be_created(self):
        response = self.client.post(
            reverse("customers:customer-create"),
            {
                "customer_name": "Kilimanjaro Grocers",
                "customer_phone": "+255 700 000001",
                "customer_location": "Moshi",
                "notes": "",
            },
        )

        self.assertRedirects(response, reverse("customers:customer-list"))
        self.assertTrue(
            Customer.objects.filter(customer_name="Kilimanjaro Grocers").exists()
        )

    def test_customer_form_requires_name_and_phone(self):
        form = CustomerForm(
            data={
                "customer_name": "",
                "customer_phone": "",
                "customer_location": "",
                "notes": "",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("customer_name", form.errors)
        self.assertIn("customer_phone", form.errors)

    def test_customer_detail_shows_order_history(self):
        crop = Crop.objects.create(
            crop_name="Tomatoes",
            maturity_days=60,
            unit="kg",
        )
        order = Order.objects.create(
            customer=self.customer,
            order_date=date(2026, 10, 1),
        )
        OrderItem.objects.create(
            order=order,
            crop=crop,
            quantity=Decimal("3.00"),
            unit_price=Decimal("2000.00"),
        )

        response = self.client.get(
            reverse("customers:customer-detail", args=[self.customer.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Weekly buyer")
        self.assertContains(response, f"#{order.pk}")
        self.assertContains(response, "Tomatoes (3.00)")

    def test_customer_can_be_updated(self):
        response = self.client.post(
            reverse("customers:customer-update", args=[self.customer.pk]),
            {
                "customer_name": "Amina Produce",
                "customer_phone": "+255 700 123456",
                "customer_location": "Arusha",
                "notes": "Updated notes",
            },
        )

        self.assertRedirects(response, reverse("customers:customer-list"))
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.customer_name, "Amina Produce")
        self.assertEqual(self.customer.notes, "Updated notes")

    def test_customer_without_order_history_can_be_deleted(self):
        response = self.client.post(
            reverse("customers:customer-delete", args=[self.customer.pk])
        )

        self.assertRedirects(response, reverse("customers:customer-list"))
        self.assertFalse(Customer.objects.filter(pk=self.customer.pk).exists())

    def test_customer_with_order_history_cannot_be_deleted(self):
        Order.objects.create(
            customer=self.customer,
            order_date=date(2026, 10, 1),
        )

        response = self.client.post(
            reverse("customers:customer-delete", args=[self.customer.pk])
        )

        self.assertEqual(response.status_code, 409)
        self.assertContains(response, "cannot be deleted", status_code=409)
        self.assertTrue(Customer.objects.filter(pk=self.customer.pk).exists())

    def test_delete_confirmation_explains_order_history_protection(self):
        Order.objects.create(
            customer=self.customer,
            order_date=date(2026, 10, 1),
        )

        response = self.client.get(
            reverse("customers:customer-delete", args=[self.customer.pk])
        )

        self.assertContains(response, "cannot be deleted")
        self.assertNotContains(response, "Yes, delete customer")
