"""Focused tests for Django's user-facing HTTP error responses."""

import sys
from types import ModuleType

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import path, reverse

from apps.crops.models import Crop, Field, Planting
from apps.harvests.models import Harvest


def raise_controlled_error(request):
    """Raise a test-only error to exercise Django's production 500 handler."""
    raise RuntimeError("private diagnostic detail")


_ERROR_URLCONF_NAME = "config.test_error_urls"
_error_urlconf = ModuleType(_ERROR_URLCONF_NAME)
_error_urlconf.urlpatterns = [
    path("controlled-error/", raise_controlled_error),
]
sys.modules[_ERROR_URLCONF_NAME] = _error_urlconf


@override_settings(DEBUG=False)
class HttpErrorPageTests(TestCase):
    """Keep standard error pages separate from normal workflow validation."""

    @classmethod
    def setUpTestData(cls):
        cls.admin = get_user_model().objects.create_superuser(
            username="error-page-admin",
            email="error-page-admin@example.test",
            password="test-password-for-error-pages",
        )
        cls.crop = Crop.objects.create(
            crop_name="Tomatoes",
            maturity_days=60,
            unit=Crop.Unit.KILOGRAM,
        )
        cls.field = Field.objects.create(
            field_name="Error test field",
            field_size="1.00",
        )
        cls.planting = Planting.objects.create(
            crop=cls.crop,
            field=cls.field,
            planting_qty_unit="seeds",
            quantity_planted="10.00",
            planting_date="2026-10-01",
        )
        cls.harvest = Harvest.objects.create(
            planting=cls.planting,
            harvesting_date="2026-10-02",
            quantity_harvested="1.00",
            unit=cls.crop.unit,
        )

    def test_bad_request_uses_standalone_400_template(self):
        response = Client().get("/", HTTP_HOST="invalid.example")

        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, "400.html")
        self.assertContains(
            response,
            "Check the information you submitted",
            status_code=400,
        )
        self.assertContains(response, 'href="/"', status_code=400)
        self.assertNotContains(response, "invalid.example", status_code=400)

    def test_unknown_url_uses_standalone_404_template(self):
        response = Client().get("/this-page-does-not-exist/secret-value")

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")
        self.assertContains(
            response,
            "We couldn't find that page",
            status_code=404,
        )
        self.assertContains(response, 'href="/"', status_code=404)
        self.assertNotContains(response, "secret-value", status_code=404)

    def test_missing_crop_field_planting_and_harvest_resources_return_404(self):
        self.client.force_login(self.admin)
        missing_urls = (
            reverse("crops:crop-detail", args=[999999]),
            reverse("crops:field-detail", args=[999999]),
            reverse("crops:planting-detail", args=[999999]),
            reverse("harvests:harvest-update", args=[999999]),
        )

        for url in missing_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 404)
                self.assertTemplateUsed(response, "404.html")

    def test_user_without_required_permission_gets_friendly_403(self):
        user = get_user_model().objects.create_user(
            username="no-crop-permission",
            password="test-password-for-error-pages",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("crops:crop-list"))

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "403.html")
        self.assertContains(
            response,
            "You don't have access to this page",
            status_code=403,
        )
        self.assertContains(response, 'href="/"', status_code=403)

    def test_anonymous_user_keeps_existing_login_redirect(self):
        response = self.client.get(reverse("crops:crop-list"))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("accounts:login")))

    def test_invalid_crop_form_stays_on_form_and_displays_validation_errors(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse("crops:crop-create"),
            {
                "crop_name": "",
                "maturity_days": "60",
                "unit": Crop.Unit.KILOGRAM,
                "description": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "crops/crop_form.html")
        self.assertContains(response, "This field is required.")
        self.assertContains(response, 'name="maturity_days" value="60"')
        self.assertFalse(Crop.objects.filter(crop_name="").exists())

    def test_csrf_invalid_post_is_rejected_with_friendly_guidance(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.admin)

        response = csrf_client.post(reverse("accounts:logout"))

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "403_csrf.html")
        self.assertContains(response, "refresh the page", status_code=403)
        self.assertContains(response, 'href="/"', status_code=403)

    @override_settings(ROOT_URLCONF=_ERROR_URLCONF_NAME)
    def test_unexpected_exception_returns_generic_500_without_details(self):
        error_client = Client(raise_request_exception=False)

        response = error_client.get("/controlled-error/")

        self.assertEqual(response.status_code, 500)
        self.assertTemplateUsed(response, "500.html")
        self.assertContains(
            response,
            "An unexpected error occurred",
            status_code=500,
        )
        self.assertContains(response, 'href="/"', status_code=500)
        self.assertNotContains(
            response,
            "private diagnostic detail",
            status_code=500,
        )

    def test_root_redirect_remains_available(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse("dashboard:dashboard"),
            fetch_redirect_response=False,
        )
