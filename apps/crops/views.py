from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)

from .models import Planting
from .forms import PlantingForm


class PlantingListView(ListView):
    """This page is responsible for displaying a collection of Planting objects."""
    model = Planting
    template_name = "crops/planting_list.html"
    context_object_name = "plantings"

    def get_queryset(self):
        return (
            Planting.objects
            .select_related("crop", "field")
            .order_by("-planting_date")
        )


class PlantingDetailView(DetailView):
    model = Planting
    template_name = "crops/planting_detail.html"
    context_object_name = "planting"


class PlantingCreateView(CreateView):
    model = Planting
    form_class = PlantingForm
    template_name = "crops/planting_form.html"
    success_url = reverse_lazy("crops:planting-list")


class PlantingUpdateView(UpdateView):
    model = Planting
    form_class = PlantingForm
    template_name = "crops/planting_form.html"
    success_url = reverse_lazy("crops:planting-list")


class PlantingDeleteView(DeleteView):
    model = Planting
    template_name = "crops/planting_confirm_delete.html"
    context_object_name = "planting"
    success_url = reverse_lazy("crops:planting-list")