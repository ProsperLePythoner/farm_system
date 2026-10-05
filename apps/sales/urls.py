from django.urls import path

from . import views

app_name = "sales"

urlpatterns = [
    path("", views.OrderListView.as_view(), name="order-list"),
    path("orders/new/", views.OrderCreateView.as_view(), name="order-create"),
    path("orders/<int:pk>/", views.OrderDetailView.as_view(), name="order-detail"),
    path("orders/<int:pk>/edit/", views.OrderUpdateView.as_view(), name="order-update"),
    path("orders/<int:pk>/delete/", views.OrderDeleteView.as_view(), name="order-delete"),
]