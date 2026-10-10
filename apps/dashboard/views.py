from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from apps.accounts.permissions import ApplicationRoleRequiredMixin


class DashboardView(LoginRequiredMixin, ApplicationRoleRequiredMixin, TemplateView):
    template_name = "dashboard/dashboard.html"