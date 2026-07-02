from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    path("sales/", include("apps.sales.urls")),
    path("crops/", include("apps.crops.urls")),
    path("customers/", include("apps.customers.urls")),
    path("harvests/", include("apps.harvests.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
]