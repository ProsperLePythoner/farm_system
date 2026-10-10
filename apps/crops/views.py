from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Count, Prefetch
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    TemplateView,
    UpdateView,
)
from django.views.generic.list import ListView

from apps.harvests.models import Harvest

from config.view_mixins import ProtectedDeleteMixin

from .forms import CropForm, FieldForm, PlantingForm
from .models import Crop, Field, Planting


class CropsOverviewView(PermissionRequiredMixin, TemplateView):
    permission_required = (
        "crops.view_crop",
        "crops.view_field",
        "crops.view_planting",
    )
    template_name = "crops/overview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "crop_count": Crop.objects.count(),
            "field_count": Field.objects.count(),
            "planting_count": Planting.objects.count(),
            "recent_plantings": (
                Planting.objects.select_related("crop", "field")
                .order_by("-planting_date", "-pk")[:5]
            ),
        })
        return context


class CropListView(PermissionRequiredMixin, ListView):
    permission_required = ("crops.view_crop", "crops.view_planting")
    model = Crop
    template_name = "crops/crop_list.html"
    context_object_name = "crops"
    queryset = Crop.objects.annotate(
        planting_count=Count("plantings")
    ).order_by("crop_name", "pk")


class CropDetailView(PermissionRequiredMixin, DetailView):
    permission_required = (
        "crops.view_crop",
        "crops.view_planting",
        "crops.view_field",
    )
    model = Crop
    template_name = "crops/crop_detail.html"
    context_object_name = "crop"

    def get_queryset(self):
        return Crop.objects.prefetch_related(
            Prefetch(
                "plantings",
                queryset=Planting.objects.select_related("field").order_by("-planting_date", "-pk"),
            )
        )


class FieldListView(PermissionRequiredMixin, ListView):
    permission_required = ("crops.view_field", "crops.view_planting")
    model = Field
    template_name = "crops/field_list.html"
    context_object_name = "fields"
    queryset = Field.objects.annotate(
        planting_count=Count("plantings")
    ).order_by("field_name", "pk")


class FieldDetailView(PermissionRequiredMixin, DetailView):
    permission_required = (
        "crops.view_field",
        "crops.view_planting",
        "crops.view_crop",
    )
    model = Field
    template_name = "crops/field_detail.html"
    context_object_name = "field"

    def get_queryset(self):
        return Field.objects.prefetch_related(
            Prefetch(
                "plantings",
                queryset=Planting.objects.select_related("crop").order_by("-planting_date", "-pk"),
            )
        )


class ProtectedDeleteView(PermissionRequiredMixin, ProtectedDeleteMixin, DeleteView):
    blocked_message = "This record is in use and cannot be deleted."


class CropCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = "crops.add_crop"
    model = Crop
    form_class = CropForm
    template_name = "crops/crop_form.html"
    success_url = reverse_lazy("crops:crop-list")
    success_message = "Crop created."


class CropUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = ("crops.change_crop", "crops.view_planting")
    model = Crop
    form_class = CropForm
    template_name = "crops/crop_form.html"
    context_object_name = "crop"
    success_url = reverse_lazy("crops:crop-list")
    success_message = "Crop updated."


class CropDeleteView(ProtectedDeleteView):
    permission_required = "crops.delete_crop"
    model = Crop
    template_name = "crops/crop_confirm_delete.html"
    context_object_name = "crop"
    success_url = reverse_lazy("crops:crop-list")
    deleted_message = "Crop deleted."
    blocked_message = "This crop has plantings or sales and cannot be deleted."

    def is_deletion_blocked(self):
        return (
            self.object.plantings.exists()
            or self.object.order_items.exists()
        )


class FieldCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = "crops.add_field"
    model = Field
    form_class = FieldForm
    template_name = "crops/field_form.html"
    success_url = reverse_lazy("crops:field-list")
    success_message = "Field created."


class FieldUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = ("crops.change_field", "crops.view_planting")
    model = Field
    form_class = FieldForm
    template_name = "crops/field_form.html"
    context_object_name = "field"
    success_url = reverse_lazy("crops:field-list")
    success_message = "Field updated."


class FieldDeleteView(ProtectedDeleteView):
    permission_required = "crops.delete_field"
    model = Field
    template_name = "crops/field_confirm_delete.html"
    context_object_name = "field"
    success_url = reverse_lazy("crops:field-list")
    deleted_message = "Field deleted."
    blocked_message = "This field has plantings and cannot be deleted."

    def is_deletion_blocked(self):
        return self.object.plantings.exists()


class PlantingListView(PermissionRequiredMixin, ListView):
    permission_required = (
        "crops.view_planting",
        "crops.view_crop",
        "crops.view_field",
    )
    model = Planting
    template_name = "crops/planting_list.html"
    context_object_name = "plantings"

    def get_queryset(self):
        return (
            Planting.objects
            .select_related("crop", "field")
            .order_by("-planting_date", "-pk")
        )


class PlantingDetailView(PermissionRequiredMixin, DetailView):
    permission_required = (
        "crops.view_planting",
        "crops.view_crop",
        "crops.view_field",
        "harvests.view_harvest",
    )
    model = Planting
    template_name = "crops/planting_detail.html"
    context_object_name = "planting"

    def get_queryset(self):
        return (
            Planting.objects
            .select_related("crop", "field")
            .prefetch_related(
                Prefetch(
                    "harvests",
                    queryset=Harvest.objects.order_by("-harvesting_date", "-pk"),
                )
            )
        )


class PlantingCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = ("crops.add_planting", "crops.view_crop", "crops.view_field")
    model = Planting
    form_class = PlantingForm
    template_name = "crops/planting_form.html"
    success_url = reverse_lazy("crops:planting-list")
    success_message = "Planting created."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["has_crops"] = Crop.objects.exists()
        context["has_fields"] = Field.objects.exists()
        return context


class PlantingUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = (
        "crops.change_planting",
        "crops.view_crop",
        "crops.view_field",
    )
    model = Planting
    form_class = PlantingForm
    template_name = "crops/planting_form.html"
    context_object_name = "planting"
    success_url = reverse_lazy("crops:planting-list")
    success_message = "Planting updated."


class PlantingDeleteView(ProtectedDeleteView):
    permission_required = "crops.delete_planting"
    model = Planting
    template_name = "crops/planting_confirm_delete.html"
    context_object_name = "planting"
    success_url = reverse_lazy("crops:planting-list")
    deleted_message = "Planting deleted."
    blocked_message = "This planting has harvest records and cannot be deleted."

    def is_deletion_blocked(self):
        return self.object.harvests.exists()
