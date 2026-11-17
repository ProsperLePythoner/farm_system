"""Send, or preview, the daily farm briefing emails.

Examples
    python manage.py send_reminders --dry-run          # print, send nothing
    python manage.py send_reminders --date 2026-11-02  # preview another day
    python manage.py send_reminders                    # send for real

The same function runs on a schedule through the cron endpoint; this command is
for testing the wording and recipients before turning email on.
"""

from datetime import date

from django.core.management.base import BaseCommand, CommandError

from apps.dashboard.reminders import build_digests, send_daily_digests


class Command(BaseCommand):
    help = "Send (or with --dry-run, print) the daily harvest and payment briefing."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Print the emails instead of sending them.")
        parser.add_argument("--date", help="Pretend today is this date (YYYY-MM-DD).")

    def handle(self, *args, **options):
        today = None
        if options["date"]:
            try:
                today = date.fromisoformat(options["date"])
            except ValueError as exc:
                raise CommandError("--date must look like 2026-11-02") from exc

        if options["dry_run"]:
            digests = build_digests(today)
            if not digests:
                self.stdout.write("No one has anything to act on; no emails would be sent.")
            for user, subject, text in digests:
                self.stdout.write(
                    f"\n=== To: {user.get_username()} <{user.email}>\n=== Subject: {subject}\n\n{text}"
                )
            self.stdout.write(self.style.SUCCESS(f"\n{len(digests)} email(s) would be sent."))
            return

        result = send_daily_digests(today)
        style = self.style.SUCCESS if not result["failed"] else self.style.ERROR
        self.stdout.write(
            style(f"Recipients: {result['recipients']}, sent: {result['sent']}, failed: {result['failed']}")
        )