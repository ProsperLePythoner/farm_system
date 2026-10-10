from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, ListView, UpdateView

from .forms import ProfileForm, UserCreateForm, UserUpdateForm
from .permissions import AccountAdministratorRequiredMixin, is_account_administrator
from .roles import ROLE_ADMINISTRATOR, ROLE_NAMES

User = get_user_model()


class AccountLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, "You are now signed in.")
        return super().form_valid(form)


class AccountLogoutView(LogoutView):
    next_page = reverse_lazy("accounts:login")
    http_method_names = ["post", "options"]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        messages.success(request, "You have been signed out.")
        return response


class ProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("accounts:profile")
    success_message = "Your profile was updated."

    def get_object(self, queryset=None):
        return self.request.user


class UserListView(
    LoginRequiredMixin,
    AccountAdministratorRequiredMixin,
    ListView,
):
    model = User
    template_name = "accounts/user_list.html"
    context_object_name = "managed_users"
    queryset = User.objects.prefetch_related("groups").order_by("username")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for managed_user in context["managed_users"]:
            managed_user.account_role = next(
                (
                    group.name
                    for group in managed_user.groups.all()
                    if group.name in ROLE_NAMES
                ),
                "",
            )
            managed_user.can_be_managed = (
                managed_user.pk != self.request.user.pk
                and can_manage_user(self.request.user, managed_user)
            )
            managed_user.can_be_toggled = (
                managed_user.pk != self.request.user.pk
                and can_manage_user(self.request.user, managed_user)
            )
        return context


class UserCreateView(
    LoginRequiredMixin,
    AccountAdministratorRequiredMixin,
    SuccessMessageMixin,
    CreateView,
):
    model = User
    form_class = UserCreateForm
    template_name = "accounts/user_form.html"
    success_url = reverse_lazy("accounts:user-list")
    success_message = "User account created."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request_user"] = self.request.user
        return kwargs


def is_trusted_administrator(user):
    return user.is_superuser or user.groups.filter(name=ROLE_ADMINISTRATOR).exists()


def active_trusted_administrator_count():
    return (
        User.objects.filter(is_active=True)
        .filter(Q(is_superuser=True) | Q(groups__name=ROLE_ADMINISTRATOR))
        .distinct()
        .count()
    )


def can_manage_user(request_user, target_user):
    if request_user.is_superuser:
        return True
    return (
        target_user.pk != request_user.pk
        and not target_user.is_superuser
        and not target_user.groups.filter(name=ROLE_ADMINISTRATOR).exists()
    )


class UserUpdateView(
    LoginRequiredMixin,
    AccountAdministratorRequiredMixin,
    SuccessMessageMixin,
    UpdateView,
):
    model = User
    form_class = UserUpdateForm
    template_name = "accounts/user_form.html"
    context_object_name = "managed_user"
    success_url = reverse_lazy("accounts:user-list")
    success_message = "User account updated."

    def get_object(self, queryset=None):
        target_user = super().get_object(queryset)
        if not can_manage_user(self.request.user, target_user):
            raise PermissionDenied
        return target_user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request_user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        with transaction.atomic():
            list(User.objects.select_for_update().order_by("pk"))
            target_user = self.object
            target_user.refresh_from_db()
            for field_name in ("first_name", "last_name", "username", "is_active"):
                setattr(target_user, field_name, form.cleaned_data[field_name])
            if not can_manage_user(self.request.user, target_user):
                raise PermissionDenied
            if (
                target_user.pk == self.request.user.pk
                and not form.cleaned_data["is_active"]
            ):
                form.add_error(None, "You cannot deactivate your own account.")
                return self.form_invalid(form)
            selected_role = form.cleaned_data["role"]
            remains_trusted = (
                target_user.is_superuser
                or selected_role.name == ROLE_ADMINISTRATOR
            )
            removes_trusted_admin = (
                is_trusted_administrator(target_user)
                and (not form.cleaned_data["is_active"] or not remains_trusted)
            )
            if (
                target_user.is_active
                and removes_trusted_admin
                and active_trusted_administrator_count() <= 1
            ):
                form.add_error(
                    None,
                    "At least one active trusted administrator must remain.",
                )
                return self.form_invalid(form)
            return super().form_valid(form)


@login_required
@require_POST
def user_toggle_active(request, pk):
    if not is_account_administrator(request.user):
        raise PermissionDenied

    with transaction.atomic():
        list(User.objects.select_for_update().order_by("pk"))
        target_user = get_object_or_404(User, pk=pk)
        if target_user.pk == request.user.pk:
            messages.error(request, "You cannot deactivate your own account.")
            return redirect("accounts:user-list")
        if not can_manage_user(request.user, target_user):
            raise PermissionDenied
        if (
            target_user.is_active
            and is_trusted_administrator(target_user)
            and active_trusted_administrator_count() <= 1
        ):
            messages.error(
                request,
                "At least one active trusted administrator must remain.",
            )
        else:
            target_user.is_active = not target_user.is_active
            target_user.save(update_fields=("is_active",))
            state = "activated" if target_user.is_active else "deactivated"
            messages.success(request, f"User account {state}.")

    return redirect("accounts:user-list")
