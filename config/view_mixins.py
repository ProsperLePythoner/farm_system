from django.contrib import messages
from django.db.models.deletion import ProtectedError


class ProtectedDeleteMixin:
    blocked_message = "This record is in use and cannot be deleted."
    deleted_message = "Record deleted."

    def is_deletion_blocked(self):
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("delete_blocked", self.is_deletion_blocked())
        context.setdefault("blocked_message", self.blocked_message)
        return context

    def form_valid(self, form):
        if self.is_deletion_blocked():
            messages.error(self.request, self.blocked_message)
            return self.render_to_response(
                self.get_context_data(form=form, delete_blocked=True),
                status=409,
            )
        try:
            response = super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, self.blocked_message)
            return self.render_to_response(
                self.get_context_data(form=form, delete_blocked=True),
                status=409,
            )
        messages.success(self.request, self.deleted_message)
        return response
