"""Named route for the authenticated dashboard landing page."""

from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    # The trailing slash matters: Vercel Cron does not follow redirects, so the
    # path configured in vercel.json must match this route exactly.
    path("cron/daily-digest/", views.DailyDigestCronView.as_view(), name="cron-daily-digest"),
]