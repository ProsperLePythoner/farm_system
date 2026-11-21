"""Regression tests for the dashboard shell and root redirect."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from apps.accounts.roles import ROLE_FARM_MANAGER

from .reminders import _recipients


class DashboardTests(TestCase):
    """Ensure the landing page uses one shared document shell."""

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
        self.assertContains(
            response,
            '<link rel="icon" type="image/svg+xml" href="/static/images/farm-system-icon.svg">',
            html=False,
        )

    def test_shared_navigation_keeps_labels_with_decorative_material_symbols(self):
        response = self.client.get(reverse("dashboard:dashboard"))

        self.assertContains(response, "dashboard</span>Dashboard", html=False)
        self.assertContains(response, "grass</span>Crops", html=False)
        self.assertContains(response, "landscape</span>Fields", html=False)
        self.assertContains(response, "point_of_sale</span>Sales", html=False)
        self.assertContains(response, 'class="material-symbols-outlined" aria-hidden="true"')

    def test_shared_shell_preloads_local_inter_without_google_font_links(self):
        response = self.client.get(reverse("dashboard:dashboard"))

        self.assertContains(response, "fonts/inter/inter-latin.woff2")
        self.assertNotContains(response, "fonts.googleapis.com")
        self.assertNotContains(response, "fonts.gstatic.com")

    def test_root_redirect_uses_named_dashboard_route(self):
        response = self.client.get("/")

        self.assertRedirects(
            response,
            reverse("dashboard:dashboard"),
            fetch_redirect_response=False,
        )

    def test_farm_manager_receives_harvest_but_not_payment_digest(self):
        farm_manager = get_user_model().objects.create_user(
            username="farm-manager",
            email="farm-manager@example.test",
        )
        farm_manager.groups.add(
            Group.objects.get_or_create(name=ROLE_FARM_MANAGER)[0]
        )

        farm_manager_recipients = [
            recipient for recipient in _recipients()
            if recipient[0].pk == farm_manager.pk
        ]
        self.assertEqual(farm_manager_recipients, [(farm_manager, True, False)])
