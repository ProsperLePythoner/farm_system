from django.urls import path

from . import views

app_name = "harvests"

urlpatterns = [
    path("", views.HarvestListView.as_view(), name="harvest-list"),
    path(
        "plantings/<int:planting_pk>/new/",
        views.HarvestCreateView.as_view(),
        name="harvest-create",
    ),
    path("<int:pk>/edit/", views.HarvestUpdateView.as_view(), name="harvest-update"),
    path("<int:pk>/delete/", views.HarvestDeleteView.as_view(), name="harvest-delete"),
]