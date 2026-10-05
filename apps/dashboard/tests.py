from django.test import TestCase
from django.urls import reverse


class DashboardTests(TestCase):
    def test_dashboard_renders_through_shared_shell_once(self):
        response = self.client.get(reverse("dashboard:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Farm Dashboard")
        self.assertEqual(response.content.lower().count(b"<html"), 1)

    def test_root_redirect_uses_named_dashboard_route(self):
        response = self.client.get("/")

        self.assertRedirects(response, reverse("dashboard:dashboard"))
