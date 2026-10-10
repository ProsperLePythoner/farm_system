from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class DashboardTests(TestCase):
    def setUp(self):
        admin = get_user_model().objects.create_superuser(
            username="dashboard-admin",
            email="admin@example.test",
            password="test-password",
        )
        self.client.force_login(admin)

    def test_dashboard_renders_through_shared_shell_once(self):
        response = self.client.get(reverse("dashboard:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Farm Dashboard")
        self.assertEqual(response.content.lower().count(b"<html"), 1)

    def test_root_redirect_uses_named_dashboard_route(self):
        response = self.client.get("/")

        self.assertRedirects(
            response,
            reverse("dashboard:dashboard"),
            fetch_redirect_response=False,
        )
