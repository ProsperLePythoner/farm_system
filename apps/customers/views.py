from django.db.models import Prefetch
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from config.view_mixins import ProtectedDeleteMixin

from apps.sales.models import Order

from .forms import CustomerForm
from .models import Customer


class CustomerListView(ListView):
    model = Customer
    template_name = "customers/customer_list.html"
    context_object_name = "customers"
    queryset = Customer.objects.order_by("customer_name", "pk")


class CustomerDetailView(DetailView):
    model = Customer
    template_name = "customers/customer_detail.html"
    context_object_name = "customer"

    def get_queryset(self):
        order_history = (
            Order.objects
            .prefetch_related("items__crop")
            .order_by("-order_date", "-pk")
        )
        return Customer.objects.prefetch_related(
            Prefetch("orders", queryset=order_history)
        )


class CustomerCreateView(SuccessMessageMixin, CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = "customers/customer_form.html"
    success_url = reverse_lazy("customers:customer-list")
    success_message = "Customer created."


class CustomerUpdateView(SuccessMessageMixin, UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = "customers/customer_form.html"
    context_object_name = "customer"
    success_url = reverse_lazy("customers:customer-list")
    success_message = "Customer updated."


class CustomerDeleteView(ProtectedDeleteMixin, DeleteView):
    model = Customer
    template_name = "customers/customer_confirm_delete.html"
    context_object_name = "customer"
    success_url = reverse_lazy("customers:customer-list")
    blocked_message = "This customer has orders and cannot be deleted."
    deleted_message = "Customer deleted."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["has_order_history"] = self.is_deletion_blocked()
        return context

    def is_deletion_blocked(self):
        return self.object.orders.exists()
