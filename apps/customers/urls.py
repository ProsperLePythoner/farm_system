from django.urls import path

from . import views

app_name = "customers"

urlpatterns = [
    path("", views.CustomerListView.as_view(), name="customer-list"),
    path("new/", views.CustomerCreateView.as_view(), name="customer-create"),
    path("<int:pk>/", views.CustomerDetailView.as_view(), name="customer-detail"),
    path("<int:pk>/edit/", views.CustomerUpdateView.as_view(), name="customer-update"),
    path("<int:pk>/delete/", views.CustomerDeleteView.as_view(), name="customer-delete"),
]