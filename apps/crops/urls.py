from django.urls import path

from . import views


app_name = "crops"

urlpatterns = [
    path(
        "plantings/",
        views.PlantingListView.as_view(),
        name="planting-list",
    ),

    path(
        "plantings/new/",
        views.PlantingCreateView.as_view(),
        name="planting-create",
    ),

    path(
        "plantings/<int:pk>/",
        views.PlantingDetailView.as_view(),
        name="planting-detail",
    ),

    path(
        "plantings/<int:pk>/edit/",
        views.PlantingUpdateView.as_view(),
        name="planting-update",
    ),

    path(
        "plantings/<int:pk>/delete/",
        views.PlantingDeleteView.as_view(),
        name="planting-delete",
    ),
]