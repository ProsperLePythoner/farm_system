from django.contrib import admin
from django.views.generic import RedirectView
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", RedirectView.as_view(pattern_name="dashboard:dashboard")),

    path("sales/", include("apps.sales.urls")),
    path("crops/", include("apps.crops.urls")),
    path("customers/", include("apps.customers.urls")),
    path("harvests/", include("apps.harvests.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
    path("testing/", include("apps.testing.urls")),
]