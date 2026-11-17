"""Daily email digest of harvest windows and unpaid orders.

WHAT THIS FILE DOES
    Builds one plain-text "farm briefing" per recipient and sends it. A section
    appears only when it has something to act on, and a person with nothing to
    act on receives no email at all.

WHO GETS WHAT (the recipient rules the roadmap asked to define first)
    * Only active users who have an email address saved on their account.
    * Harvest section: Administrator, Farm Manager, Harvest Manager.
    * Payments section: Administrator, Farm Manager, Sales Manager.
    * Django superusers receive both. Staff (read-only) receive none; they can
      still see everything on the dashboard.
    Change the two role tuples below to change the rules.

WHEN
    Once a day. vercel.json schedules ``/dashboard/cron/daily-digest/`` for
    04:00 UTC (07:00 in East Africa). The Vercel Hobby plan allows one run a
    day, which suits a morning briefing.

WHAT COUNTS AS WORTH AN EMAIL
    * Harvest windows open today, windows opening within
      ``HARVEST_REMINDER_LEAD_DAYS`` days, and windows that ended in the last
      30 days with no harvest recorded.
    * Orders still unpaid ``PAYMENT_REMINDER_AFTER_DAYS`` or more days after the
      order date. A brand-new unpaid order is normal and is not nagged about.
"""

from __future__ import annotations

import logging
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from django.utils import timezone

from apps.accounts.roles import (
    ROLE_ADMINISTRATOR,
    ROLE_FARM_MANAGER,
    ROLE_HARVEST_MANAGER,
    ROLE_SALES_MANAGER,
)
from apps.sales.models import Order

from .services import harvest_section

logger = logging.getLogger(__name__)

HARVEST_RECIPIENT_ROLES = (ROLE_ADMINISTRATOR, ROLE_FARM_MANAGER, ROLE_HARVEST_MANAGER)
PAYMENT_RECIPIENT_ROLES = (ROLE_ADMINISTRATOR, ROLE_FARM_MANAGER, ROLE_SALES_MANAGER)
PAYMENT_LIST_LIMIT = 10


def _payment_after_days() -> int:
    return getattr(settings, "PAYMENT_REMINDER_AFTER_DAYS", 7)


def _money(value: Decimal) -> str:
    return f"TSh {value:,.2f}"


def _span(start, end) -> str:
    if start == end:
        return start.strftime("%d %b")
    return f"{start.strftime('%d %b')} – {end.strftime('%d %b')}"


def _overdue_orders(today):
    """Orders unpaid long enough to chase, oldest first, plus how many there are."""
    cutoff = today - timedelta(days=_payment_after_days())
    queryset = Order.objects.with_outstanding_balance().filter(order_date__lte=cutoff)
    count = queryset.count()
    orders = list(
        queryset.select_related("customer").order_by("order_date", "pk")[:PAYMENT_LIST_LIMIT]
    )
    for order in orders:
        order.days_outstanding = (today - order.order_date).days
    return orders, count


def _harvest_lines(section) -> list[str]:
    lines: list[str] = []
    if section.open:
        lines.append("Harvest window open now")
        for item in section.open:
            p = item.planting
            lines.append(
                f"  - {p.crop.crop_name} ({p.field.field_name}): "
                f"{_span(item.window_start, item.window_end)}. {item.label}."
            )
    imminent = [item for item in section.soon if item.is_imminent]
    if imminent:
        lines.append(f"Opening within {settings.HARVEST_REMINDER_LEAD_DAYS} days")
        for item in imminent:
            p = item.planting
            lines.append(
                f"  - {p.crop.crop_name} ({p.field.field_name}): "
                f"{_span(item.window_start, item.window_end)}. {item.label}."
            )
    if section.missed:
        lines.append("Window ended and no harvest was recorded")
        for item in section.missed:
            p = item.planting
            lines.append(
                f"  - {p.crop.crop_name} ({p.field.field_name}): "
                f"{_span(item.window_start, item.window_end)}."
            )
    return lines


def _payment_lines(orders, total_count) -> list[str]:
    lines = [f"Payments to collect (unpaid {_payment_after_days()}+ days)"]
    for order in orders:
        phone = order.customer.customer_phone
        lines.append(
            f"  - Order #{order.pk}, {order.customer.customer_name}"
            f"{f' ({phone})' if phone else ''}: "
            f"{_money(order.outstanding_balance)} outstanding, "
            f"{order.days_outstanding} days since order."
        )
    if total_count > len(orders):
        lines.append(f"  ...and {total_count - len(orders)} more.")
    return lines


def _recipients():
    """Active users with an email, with their role names already loaded."""
    User = get_user_model()
    users = (
        User.objects.filter(is_active=True)
        .exclude(email="")
        .prefetch_related("groups")
    )
    for user in users:
        roles = {group.name for group in user.groups.all()}
        wants_harvest = user.is_superuser or bool(roles & set(HARVEST_RECIPIENT_ROLES))
        wants_payments = user.is_superuser or bool(roles & set(PAYMENT_RECIPIENT_ROLES))
        if wants_harvest or wants_payments:
            yield user, wants_harvest, wants_payments


def build_digests(today=None):
    """Return ``[(user, subject, body), ...]`` for everyone with something to act on."""
    today = today or timezone.localdate()
    recipients = list(_recipients())
    if not recipients:
        return []

    # Query once, and only for sections somebody will actually receive.
    section = harvest_section(today) if any(r[1] for r in recipients) else None
    overdue, overdue_count = (
        _overdue_orders(today) if any(r[2] for r in recipients) else ([], 0)
    )
    harvest_lines = _harvest_lines(section) if section else []

    link = ""
    if settings.SITE_URL:
        link = f"\nOpen the dashboard: {settings.SITE_URL}{reverse('dashboard:dashboard')}\n"

    digests = []
    for user, wants_harvest, wants_payments in recipients:
        blocks: list[list[str]] = []
        subject_bits: list[str] = []
        if wants_harvest and harvest_lines:
            blocks.append(["HARVESTS"] + harvest_lines)
            needs = len(section.open) + len([i for i in section.soon if i.is_imminent])
            if needs:
                subject_bits.append(f"{needs} harvest window{'s' if needs != 1 else ''}")
            if section.missed:
                subject_bits.append(f"{len(section.missed)} unrecorded")
        if wants_payments and overdue:
            blocks.append(["PAYMENTS"] + _payment_lines(overdue, overdue_count))
            subject_bits.append(f"{overdue_count} payment{'s' if overdue_count != 1 else ''} due")
        if not blocks:
            continue  # nothing to act on: do not send an empty email

        name = user.get_full_name() or user.get_username()
        body = "\n\n".join("\n".join(block) for block in blocks)
        text = (
            f"Good morning, {name}.\n\n"
            f"Your farm briefing for {today.strftime('%A %d %B %Y')}:\n\n"
            f"{body}\n{link}"
        )
        subject = f"Farm briefing {today.strftime('%a %d %b')}: " + ", ".join(subject_bits)
        digests.append((user, subject, text))
    return digests


def send_daily_digests(today=None) -> dict:
    """Send the digests and return counts only (no addresses) for logs."""
    digests = build_digests(today)
    messages = [
        mail.EmailMessage(subject, text, settings.DEFAULT_FROM_EMAIL, [user.email])
        for user, subject, text in digests
    ]
    sent = 0
    if messages:
        try:
            with mail.get_connection() as connection:
                sent = connection.send_messages(messages) or 0
        except Exception:  # noqa: BLE001 - report instead of crashing the cron run
            logger.exception("Daily digest could not be sent")
    return {"recipients": len(messages), "sent": sent, "failed": len(messages) - sent}
