"""Permission-checked order pages with atomic save of order and its line items."""

from django.db import transaction
from django.db.models import Prefetch
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django.contrib import messages

from config.view_mixins import ProtectedDeleteMixin
from .forms import OrderForm, OrderItemFormSet, PaymentForm
from .models import Order, OrderItem, Payment


class OrderListView(PermissionRequiredMixin, ListView):
    permission_required = (
        "sales.view_order",
        "sales.view_orderitem",
        "customers.view_customer",
    )
    model = Order
    template_name = "sales/order_list.html"
    context_object_name = "orders"
    paginate_by = 25

    def get_queryset(self):
        orders = Order.objects.select_related("customer").with_totals()
        if self.payment_filter == "unpaid":
            orders = orders.filter(annotated_balance__gt=0)
        return orders.order_by("-order_date", "-pk")

    @property
    def payment_filter(self):
        # The balance column is only visible to users who may view payments, so
        # only they may filter on it.
        if self.request.GET.get("payment") == "unpaid" and self.request.user.has_perm("sales.view_payment"):
            return "unpaid"
        return ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["payment_filter"] = self.payment_filter
        context["pagination_query"] = "payment=unpaid" if self.payment_filter else ""
        return context


class OrderDetailView(PermissionRequiredMixin, DetailView):
    permission_required = (
        "sales.view_order",
        "sales.view_orderitem",
        "customers.view_customer",
        "crops.view_crop",
        "harvests.view_harvest",
    )
    model = Order
    template_name = "sales/order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
        # One joined query for items instead of several separate ones.
        items = OrderItem.objects.select_related(
            "crop", "harvest__planting__field"
        ).order_by("pk")
        payments = Payment.objects.order_by("-payment_date", "-pk")
        return (
            Order.objects
            .select_related("customer")
            .prefetch_related(
                Prefetch("items", queryset=items),
                Prefetch("payments", queryset=payments),
            )
        )


class OrderFormsetViewMixin:
    """Share inline-item formset handling between order create and edit views."""

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
        """Save the parent and items together so invalid items cannot leave a partial order."""
        item_formset = self.get_item_formset()
        if not item_formset.is_valid():
            return self.form_invalid(form)

        with transaction.atomic():
            self.object = form.save()
            item_formset.instance = self.object
            item_formset.save()
        messages.success(self.request, self.success_message)
        return redirect(self.get_success_url())


class OrderCreateView(PermissionRequiredMixin, OrderFormsetViewMixin, CreateView):
    permission_required = (
        "sales.add_order",
        "sales.add_orderitem",
        "customers.view_customer",
        "harvests.view_harvest",
        "crops.view_crop",
    )
    model = Order
    form_class = OrderForm
    template_name = "sales/order_form.html"
    success_message = "Order created."

    def get_success_url(self):
        return reverse("sales:order-detail", kwargs={"pk": self.object.pk})


class OrderUpdateView(PermissionRequiredMixin, OrderFormsetViewMixin, UpdateView):
    permission_required = (
        "sales.change_order",
        "sales.change_orderitem",
        "customers.view_customer",
        "harvests.view_harvest",
        "crops.view_crop",
    )
    model = Order
    form_class = OrderForm
    template_name = "sales/order_form.html"
    context_object_name = "order"
    success_message = "Order updated."

    def get_queryset(self):
        return Order.objects.select_related("customer").prefetch_related("items")

    def get_success_url(self):
        return reverse("sales:order-detail", kwargs={"pk": self.object.pk})


class OrderDeleteView(PermissionRequiredMixin, ProtectedDeleteMixin, DeleteView):
    """Prevent deleting orders whose payment history must be retained."""

    permission_required = ("sales.delete_order", "sales.delete_orderitem")
    model = Order
    template_name = "sales/order_confirm_delete.html"
    context_object_name = "order"
    success_url = reverse_lazy("sales:order-list")
    blocked_message = "This order has payment history and cannot be deleted."
    deleted_message = "Order deleted."

    def get_queryset(self):
        return Order.objects.select_related("customer").prefetch_related("items")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["has_payments"] = self.is_deletion_blocked()
        return context

    def is_deletion_blocked(self):
        return self.object.payments.exists()


class PaymentCreateView(PermissionRequiredMixin, CreateView):
    """Record a payment installment on one order.

    Payments are append-only here: corrections go through the Django admin so
    financial history is never edited casually.
    """

    permission_required = (
        "sales.add_payment",
        "sales.view_payment",
        "sales.view_order",
        "sales.view_orderitem",
        "customers.view_customer",
    )
    model = Payment
    form_class = PaymentForm
    template_name = "sales/payment_form.html"

    def dispatch(self, request, *args, **kwargs):
        # Permission is checked first; only then is the order looked up, so
        # unauthorised users learn nothing about which orders exist.
        if not self.has_permission():
            return super().dispatch(request, *args, **kwargs)
        self.order = get_object_or_404(
            Order.objects.select_related("customer").with_totals(),
            pk=kwargs["pk"],
        )
        if self.order.outstanding_balance <= 0:
            messages.info(request, "This order is already fully paid.")
            return redirect("sales:order-detail", pk=self.order.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["order"] = self.order
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["order"] = self.order
        return context

    def form_valid(self, form):
        """Re-check the balance under a row lock, then save.

        Two people recording a payment for the same order at the same moment
        would otherwise both pass the form's balance check against the same
        old balance and together overpay. Locking the order row makes the
        second request wait, then see the first payment.
        """
        with transaction.atomic():
            Order.objects.select_for_update().filter(pk=self.order.pk).values_list("pk").first()
            fresh = Order.objects.with_totals().get(pk=self.order.pk)
            if form.cleaned_data["amount_paid"] > fresh.outstanding_balance:
                form.add_error(
                    "amount_paid",
                    f"Another payment was just recorded. The outstanding balance is now TSh {fresh.outstanding_balance:,.2f}.",
                )
                self.order = Order.objects.select_related("customer").with_totals().get(pk=self.order.pk)
                return self.form_invalid(form)
            form.instance.order_id = self.order.pk
            self.object = form.save()
        messages.success(
            self.request,
            f"Payment of TSh {self.object.amount_paid:,.2f} recorded for order #{self.order.pk}.",
        )
        return redirect("sales:order-detail", pk=self.order.pk)
