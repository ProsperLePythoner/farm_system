"""Authenticated dashboard landing view."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from apps.accounts.permissions import ApplicationRoleRequiredMixin


class DashboardView(LoginRequiredMixin, ApplicationRoleRequiredMixin, TemplateView):
    """Render the shared-shell landing page for recognized application roles."""

    template_name = "dashboard/dashboard.html"