from django.urls import path
from . import views

app_name = "testing"

urlpatterns = [
    path("", views.testing, name="testing"),
    path("your-name/", views.get_name, name="your-name"),
    path("<str:name>/", views.say_hello, name="say_hello"),
]