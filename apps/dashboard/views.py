"""Authenticated dashboard landing view and the scheduled reminder hook."""

import hmac

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView

from apps.accounts.permissions import ApplicationRoleRequiredMixin

from .reminders import send_daily_digests


class DashboardView(LoginRequiredMixin, ApplicationRoleRequiredMixin, TemplateView):
    """Render the shared-shell landing page for recognized application roles."""

    template_name = "dashboard/dashboard.html"

class DailyDigestCronView(View):
    """Send the daily reminder emails when called by the scheduler.

    Vercel Cron issues a ``GET`` and, when a ``CRON_SECRET`` environment
    variable exists, adds ``Authorization: Bearer <secret>``. With no secret
    configured the endpoint refuses everything, so the public can never
    trigger it. The secret is compared in constant time.
    """

    http_method_names = ["get"]

    def get(self, request):
        secret = settings.CRON_SECRET
        supplied = request.headers.get("Authorization", "")
        expected = f"Bearer {secret}"
        if not secret or not hmac.compare_digest(supplied.encode(), expected.encode()):
            return JsonResponse({"detail": "Forbidden"}, status=403)
        result = send_daily_digests()
        return JsonResponse(result)
