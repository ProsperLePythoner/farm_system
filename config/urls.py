"""Root URL table: routes each public path prefix to its owning Django app."""

from django.contrib import admin
from django.views.generic import RedirectView
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    # Send the site root to the named dashboard route rather than duplicating
    # the dashboard page's URL or view here.
    path("", RedirectView.as_view(pattern_name="dashboard:dashboard")),

    # Each app owns its URL names and page handlers; these prefixes keep the
    # root table small and make reverse() calls use namespaced route names.
    path("sales/", include("apps.sales.urls")),
    path("crops/", include("apps.crops.urls")),
    path("customers/", include("apps.customers.urls")),
    path("harvests/", include("apps.harvests.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
    path("testing/", include("apps.testing.urls")),
]