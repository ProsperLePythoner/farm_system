from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from apps.crops.models import Planting
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from config.view_mixins import ProtectedDeleteMixin

from .forms import HarvestForm
from .models import Harvest


class HarvestListView(PermissionRequiredMixin, ListView):
    permission_required = (
        "harvests.view_harvest",
        "crops.view_planting",
        "crops.view_crop",
        "crops.view_field",
    )
    model = Harvest
    template_name = "harvests/harvest_list.html"
    context_object_name = "harvests"

    def get_queryset(self):
        return Harvest.objects.select_related(
            "planting__crop",
            "planting__field",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        plantings = (
            Planting.objects
            .select_related("crop", "field")
            .order_by("planting_date", "pk")
        )
        context["upcoming_plantings"] = sorted(
            [
                planting
                for planting in plantings
                if planting.harvest_end >= today
            ],
            key=lambda planting: (planting.harvest_start, planting.pk),
        )
        return context


class HarvestCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = (
        "harvests.add_harvest",
        "crops.view_planting",
        "crops.view_crop",
        "crops.view_field",
    )
    model = Harvest
    form_class = HarvestForm
    template_name = "harvests/harvest_form.html"
    success_message = "Harvest recorded."

    def dispatch(self, request, *args, **kwargs):
        self.planting = get_object_or_404(
            Planting.objects.select_related("crop", "field"),
            pk=kwargs["planting_pk"],
        )
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = Harvest(planting=self.planting)
        return kwargs

    def form_valid(self, form):
        form.instance.planting = self.planting
        form.instance.unit = self.planting.crop.unit
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["planting"] = self.planting
        return context

    def get_success_url(self):
        return reverse("crops:planting-detail", kwargs={"pk": self.planting.pk})


class HarvestUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = (
        "harvests.change_harvest",
        "crops.view_planting",
        "crops.view_crop",
        "crops.view_field",
    )
    model = Harvest
    form_class = HarvestForm
    template_name = "harvests/harvest_form.html"
    context_object_name = "harvest"
    success_message = "Harvest updated."

    def get_queryset(self):
        return Harvest.objects.select_related("planting__crop", "planting__field")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["planting"] = self.object.planting
        return context

    def get_success_url(self):
        return reverse(
            "crops:planting-detail",
            kwargs={"pk": self.object.planting_id},
        )


class HarvestDeleteView(PermissionRequiredMixin, ProtectedDeleteMixin, DeleteView):
    permission_required = (
        "harvests.delete_harvest",
        "crops.view_planting",
        "crops.view_crop",
        "crops.view_field",
    )
    model = Harvest
    template_name = "harvests/harvest_confirm_delete.html"
    context_object_name = "harvest"
    blocked_message = "This harvest is referenced by a sale and cannot be deleted."
    deleted_message = "Harvest deleted."

    def get_queryset(self):
        return Harvest.objects.select_related("planting__crop", "planting__field")

    def get_success_url(self):
        return reverse(
            "crops:planting-detail",
            kwargs={"pk": self.object.planting_id},
        )

    def is_deletion_blocked(self):
        return self.object.order_items.exists()
