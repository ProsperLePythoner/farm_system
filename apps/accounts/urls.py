from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.AccountLoginView.as_view(), name="login"),
    path("logout/", views.AccountLogoutView.as_view(), name="logout"),
    path("profile/", views.ProfileUpdateView.as_view(), name="profile"),
    path("users/", views.UserListView.as_view(), name="user-list"),
    path("users/new/", views.UserCreateView.as_view(), name="user-create"),
    path("users/<int:pk>/edit/", views.UserUpdateView.as_view(), name="user-update"),
    path(
        "users/<int:pk>/toggle-active/",
        views.user_toggle_active,
        name="user-toggle-active",
    ),
]