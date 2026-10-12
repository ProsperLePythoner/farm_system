"""Shared view behavior used across apps, currently for protected deletion."""

from django.contrib import messages
from django.db.models.deletion import ProtectedError


class ProtectedDeleteMixin:
    """Refuse deletion when app rules or database relations protect a record.

    Concrete delete views provide ``is_deletion_blocked`` for a friendly
    pre-check. The database exception handler remains as a final safeguard
    against protected relations or a record changing between check and delete.
    """

    blocked_message = "This record is in use and cannot be deleted."
    deleted_message = "Record deleted."

    def is_deletion_blocked(self):
        """Return whether the concrete view's record has a known blocker."""
        return False

    def get_context_data(self, **kwargs):
        """Expose the pre-check result so confirmation templates can explain it."""
        context = super().get_context_data(**kwargs)
        context.setdefault("delete_blocked", self.is_deletion_blocked())
        context.setdefault("blocked_message", self.blocked_message)
        return context

    def form_valid(self, form):
        """Run delete checks before deleting and report blocked attempts as 409."""
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
