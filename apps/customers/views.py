from django.db.models import Prefetch
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from config.view_mixins import ProtectedDeleteMixin

from apps.sales.models import Order

from .forms import CustomerForm
from .models import Customer


class CustomerListView(PermissionRequiredMixin, ListView):
    permission_required = "customers.view_customer"
    model = Customer
    template_name = "customers/customer_list.html"
    context_object_name = "customers"
    queryset = Customer.objects.order_by("customer_name", "pk")


class CustomerDetailView(PermissionRequiredMixin, DetailView):
    permission_required = (
        "customers.view_customer",
        "sales.view_order",
        "sales.view_orderitem",
        "crops.view_crop",
    )
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


class CustomerCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = "customers.add_customer"
    model = Customer
    form_class = CustomerForm
    template_name = "customers/customer_form.html"
    success_url = reverse_lazy("customers:customer-list")
    success_message = "Customer created."


class CustomerUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = "customers.change_customer"
    model = Customer
    form_class = CustomerForm
    template_name = "customers/customer_form.html"
    context_object_name = "customer"
    success_url = reverse_lazy("customers:customer-list")
    success_message = "Customer updated."


class CustomerDeleteView(PermissionRequiredMixin, ProtectedDeleteMixin, DeleteView):
    permission_required = "customers.delete_customer"
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
