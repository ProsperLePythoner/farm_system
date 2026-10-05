from django.db import transaction
from django.db.models.deletion import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import OrderForm, OrderItemFormSet
from .models import Order


class OrderListView(ListView):
    model = Order
    template_name = "sales/order_list.html"
    context_object_name = "orders"
    queryset = (
        Order.objects
        .select_related("customer")
        .prefetch_related("items__crop")
        .order_by("-order_date", "-pk")
    )


class OrderDetailView(DetailView):
    model = Order
    template_name = "sales/order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
        return (
            Order.objects
            .select_related("customer")
            .prefetch_related("items__crop", "items__harvest__planting__field")
            .prefetch_related("payments")
        )


class OrderFormsetViewMixin:
    def get_item_formset(self):
        instance = self.object if getattr(self, "object", None) else Order()
        return OrderItemFormSet(
            data=self.request.POST if self.request.method == "POST" else None,
            instance=instance,
            prefix="items",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("item_formset", self.get_item_formset())
        return context

    def form_valid(self, form):
        item_formset = self.get_item_formset()
        if not item_formset.is_valid():
            return self.form_invalid(form)

        with transaction.atomic():
            self.object = form.save()
            item_formset.instance = self.object
            item_formset.save()
        return redirect(self.get_success_url())


class OrderCreateView(OrderFormsetViewMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = "sales/order_form.html"

    def get_success_url(self):
        return reverse("sales:order-detail", kwargs={"pk": self.object.pk})


class OrderUpdateView(OrderFormsetViewMixin, UpdateView):
    model = Order
    form_class = OrderForm
    template_name = "sales/order_form.html"
    context_object_name = "order"

    def get_queryset(self):
        return Order.objects.select_related("customer").prefetch_related("items")

    def get_success_url(self):
        return reverse("sales:order-detail", kwargs={"pk": self.object.pk})


class OrderDeleteView(DeleteView):
    model = Order
    template_name = "sales/order_confirm_delete.html"
    context_object_name = "order"
    success_url = reverse_lazy("sales:order-list")

    def get_queryset(self):
        return Order.objects.select_related("customer").prefetch_related("items")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["has_payments"] = self.object.payments.exists()
        return context

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except ProtectedError:
            context = self.get_context_data(
                form=form,
                has_payments=True,
            )
            return self.render_to_response(context, status=409)