from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from apps.crops.models import Planting

from .forms import HarvestForm
from .models import Harvest


class HarvestListView(ListView):
    model = Harvest
    template_name = "harvests/harvest_list.html"
    context_object_name = "harvests"

    def get_queryset(self):
        return Harvest.objects.select_related(
            "planting__crop",
            "planting__field",
        )


class HarvestCreateView(CreateView):
    model = Harvest
    form_class = HarvestForm
    template_name = "harvests/harvest_form.html"

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


class HarvestUpdateView(UpdateView):
    model = Harvest
    form_class = HarvestForm
    template_name = "harvests/harvest_form.html"
    context_object_name = "harvest"

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


class HarvestDeleteView(DeleteView):
    model = Harvest
    template_name = "harvests/harvest_confirm_delete.html"
    context_object_name = "harvest"

    def get_queryset(self):
        return Harvest.objects.select_related("planting__crop", "planting__field")

    def get_success_url(self):
        return reverse(
            "crops:planting-detail",
            kwargs={"pk": self.object.planting_id},
        )
