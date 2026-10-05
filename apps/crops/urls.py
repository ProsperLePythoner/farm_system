from django.urls import path

from . import views


app_name = "crops"

urlpatterns = [
    path("", views.CropsOverviewView.as_view(), name="overview"),
    path("crops/", views.CropListView.as_view(), name="crop-list"),
    path("crops/new/", views.CropCreateView.as_view(), name="crop-create"),
    path("crops/<int:pk>/", views.CropDetailView.as_view(), name="crop-detail"),
    path("crops/<int:pk>/edit/", views.CropUpdateView.as_view(), name="crop-update"),
    path("crops/<int:pk>/delete/", views.CropDeleteView.as_view(), name="crop-delete"),
    path("fields/", views.FieldListView.as_view(), name="field-list"),
    path("fields/new/", views.FieldCreateView.as_view(), name="field-create"),
    path("fields/<int:pk>/", views.FieldDetailView.as_view(), name="field-detail"),
    path("fields/<int:pk>/edit/", views.FieldUpdateView.as_view(), name="field-update"),
    path("fields/<int:pk>/delete/", views.FieldDeleteView.as_view(), name="field-delete"),
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