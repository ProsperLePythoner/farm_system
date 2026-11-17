"""Forms for editing a user's own profile and managing application accounts."""

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group

from .roles import ROLE_ADMINISTRATOR, ROLE_NAMES

User = get_user_model()

EMAIL_HELP = "Optional. Used for the daily farm briefing email."


class EmailNormalizationMixin:
    """Store email addresses trimmed and in lower case.

    Django calls ``clean_<fieldname>`` automatically, so any form that has an
    ``email`` field and lists this mixin first gets the behaviour.
    """

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()


class ProfileForm(EmailNormalizationMixin, forms.ModelForm):
    """Limit self-service profile changes to the user's display names."""

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
        help_texts = {"email": EMAIL_HELP}

    def clean_first_name(self):
        return self.cleaned_data["first_name"].strip()

    def clean_last_name(self):
        return self.cleaned_data["last_name"].strip()


class UserCreateForm(EmailNormalizationMixin, UserCreationForm):
    """Create a user with one role and an explicit activation choice."""

    role = forms.ModelChoiceField(
        queryset=Group.objects.none(),
        label="Role",
    )
    is_active = forms.BooleanField(
        required=False,
        initial=False,
        label="Active immediately (allow sign-in)",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("first_name", "last_name", "username", "email")
        help_texts = {"email": EMAIL_HELP}

    def __init__(self, *args, request_user, **kwargs):
        """Keep the Administrator role assignable only by a Django superuser."""
        super().__init__(*args, **kwargs)
        role_names = ROLE_NAMES
        if not request_user.is_superuser:
            role_names = tuple(
                name for name in role_names if name != ROLE_ADMINISTRATOR
            )
        self.fields["role"].queryset = Group.objects.filter(name__in=role_names)

    def clean_first_name(self):
        return self.cleaned_data["first_name"].strip()

    def clean_last_name(self):
        return self.cleaned_data["last_name"].strip()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = self.cleaned_data["is_active"]
        if commit:
            user.save()
            user.groups.set((self.cleaned_data["role"],))
        return user


class UserUpdateForm(EmailNormalizationMixin, forms.ModelForm):
    """Edit account details, activation, and one application role."""

    role = forms.ModelChoiceField(
        queryset=Group.objects.none(),
        label="Role",
    )
    is_active = forms.BooleanField(required=False, label="Active")

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email", "is_active")
        help_texts = {"email": EMAIL_HELP}

    def __init__(self, *args, request_user, **kwargs):
        """Limit role choices and initialize the user's current role."""
        super().__init__(*args, **kwargs)
        role_names = ROLE_NAMES
        if not request_user.is_superuser:
            role_names = tuple(
                name for name in role_names if name != ROLE_ADMINISTRATOR
            )
        self.fields["role"].queryset = Group.objects.filter(name__in=role_names)
        current_role = self.instance.groups.filter(name__in=role_names).first()
        if current_role:
            self.initial["role"] = current_role

    def clean_first_name(self):
        return self.cleaned_data["first_name"].strip()

    def clean_last_name(self):
        return self.cleaned_data["last_name"].strip()

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            user.groups.set((self.cleaned_data["role"],))
        return user
