"""Authenticated dashboard page, its auto-refresh fragment and the cron hook."""

import hashlib
import hmac

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseNotModified, JsonResponse
from django.template.loader import render_to_string
from django.views import View
from django.views.generic import TemplateView

from apps.accounts.permissions import ApplicationRoleRequiredMixin

from .reminders import send_daily_digests
from .services import build_dashboard


class DashboardView(LoginRequiredMixin, ApplicationRoleRequiredMixin, TemplateView):
    """Render the operational dashboard for recognized application roles.

    The page shows the same panels that ``DashboardPanelsView`` serves for the
    quiet background refresh, so what a user sees after a refresh is exactly
    what a fresh page load would show.
    """

    template_name = "dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(build_dashboard(self.request.user))
        context["refresh_seconds"] = settings.DASHBOARD_REFRESH_SECONDS
        return context


class DashboardPanelsView(LoginRequiredMixin, ApplicationRoleRequiredMixin, View):
    """Return just the dashboard panels as HTML for the page to swap in.

    The browser polls this while the dashboard tab is visible. An ``ETag`` of
    the rendered HTML lets an unchanged dashboard answer with an empty
    ``304 Not Modified``, which saves bandwidth on slow mobile connections.
    ``Cache-Control: private, no-cache`` stops shared caches from ever storing
    one user's figures and makes the browser revalidate each time.
    """

    def get(self, request):
        html = render_to_string(
            "dashboard/_panels.html",
            build_dashboard(request.user),
            request=request,
        )
        etag = '"%s"' % hashlib.sha1(html.encode("utf-8")).hexdigest()
        if request.headers.get("If-None-Match") == etag:
            response = HttpResponseNotModified()
        else:
            response = HttpResponse(html)
        response["ETag"] = etag
        response["Cache-Control"] = "private, no-cache"
        return response


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
        # A non-2xx status makes a failed run show up as failed in Vercel's
        # Cron Jobs page and logs instead of looking like a success.
        status = 502 if result["failed"] else 200
        return JsonResponse(result, status=status)