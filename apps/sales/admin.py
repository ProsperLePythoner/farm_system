# sales/admin.py

from django.contrib import admin

from .forms import OrderItemForm
from .models import Order, OrderItem, Payment


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    form = OrderItemForm
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("customer", "order_date", "total_amount", "outstanding_balance")
    list_select_related = ("customer",)
    inlines = (OrderItemInline,)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    form = OrderItemForm
    list_display = ("order", "crop", "harvest", "quantity", "unit", "unit_price")
    list_select_related = ("order", "crop", "harvest")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "payment_date", "amount_paid")
    list_select_related = ("order",)