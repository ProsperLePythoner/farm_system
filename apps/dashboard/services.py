"""Data for the operational dashboard and the daily email briefing.

WHAT THIS FILE DOES
    Turns plantings and their recorded harvests into the short, ranked lists a
    farm manager acts on each morning: harvest windows that are open or starting
    soon, and windows that ended with nothing recorded.

WHERE IT FITS
    ``reminders.py`` (the daily email) and, later, the dashboard views call the
    same functions, so the page and the email can never disagree.

KEY DECISIONS
    * Everything is derived from data that already exists (planting date, crop
      maturity, recorded harvests). Nothing here invents new business rules, in
      line with docs/roadmap.md.
    * "Missed" is deliberately worded as "window ended, nothing recorded",
      because a harvest may simply not have been entered yet.
    * The database does the date arithmetic and filtering (see
      ``Planting.objects.with_harvest_window``), and this file needs only one
      query.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal

from django.conf import settings
from django.db.models import Count, ExpressionWrapper, F, Sum
from django.utils import timezone

from apps.crops.models import Planting
from apps.sales.models import MONEY, Order, OrderItem, Payment

# How far ahead the harvest agenda looks, and how far back a "nothing recorded"
# window is still worth nagging about (older ones are history, not tasks).
AGENDA_DAYS = 14
MISSED_LOOKBACK_DAYS = 30

UNPAID_LIST_LIMIT = 8

# A section is built only for users who hold the permissions that the matching
# pages already require, so the dashboard never shows more than a user could
# open elsewhere in the application.
HARVEST_PERMS = (
    "crops.view_planting",
    "crops.view_crop",
    "crops.view_field",
    "harvests.view_harvest",
)
SALES_PERMS = (
    "sales.view_order",
    "sales.view_orderitem",
    "customers.view_customer",
)


@dataclass
class HarvestItem:
    """One planting's position relative to its calculated harvest window."""

    planting: Planting
    status: str  # "open", "soon" or "missed"
    window_start: date
    window_end: date
    days: int  # open: days left; soon: days until start; missed: days since end
    harvest_count: int
    is_imminent: bool = False  # "soon" items opening within the reminder lead time

    @property
    def label(self) -> str:
        if self.status == "open":
            if self.days == 0:
                return "Window ends today"
            return f"{self.days} day{'s' if self.days != 1 else ''} left in window"
        if self.status == "soon":
            if self.days == 1:
                return "Window opens tomorrow"
            return f"Window opens in {self.days} days"
        return (
            f"Window ended {self.days} day{'s' if self.days != 1 else ''} ago, "
            "nothing recorded"
        )


@dataclass
class AgendaDay:
    """One cell of the 14-day harvest strip."""

    day: date
    is_today: bool
    crops: list[str] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.crops)


@dataclass
class HarvestSection:
    open: list[HarvestItem]
    soon: list[HarvestItem]
    missed: list[HarvestItem]
    agenda: list[AgendaDay]

    @property
    def attention_count(self) -> int:
        return len(self.open) + len(self.missed)

@dataclass
class SalesSection:
    month_label: str
    month_sales: Decimal
    show_payments: bool
    collected_this_month: Decimal = Decimal("0.00")
    outstanding_total: Decimal = Decimal("0.00")
    unpaid_count: int = 0
    unpaid_orders: list = field(default_factory=list)


def can_see_harvests(user) -> bool:
    return user.has_perms(HARVEST_PERMS)


def can_see_sales(user) -> bool:
    return user.has_perms(SALES_PERMS)

def harvest_section(today: date, lead_days: int | None = None) -> HarvestSection:
    """Classify plantings as open, soon or missed with a single query.

    The database keeps only plantings that could matter (window ends within the
    look-back period or starts within the agenda period), so the amount of work
    does not grow as old plantings accumulate.
    """
    if lead_days is None:
        lead_days = settings.HARVEST_REMINDER_LEAD_DAYS
    horizon = today + timedelta(days=AGENDA_DAYS - 1)
    oldest = today - timedelta(days=MISSED_LOOKBACK_DAYS)

    plantings = (
        Planting.objects.select_related("crop", "field")
        .with_harvest_window()
        .filter(window_end__gte=oldest, window_start__lte=horizon)
        .annotate(harvest_count=Count("harvests"))
        .order_by("window_start", "pk")
    )

    opened: list[HarvestItem] = []
    soon: list[HarvestItem] = []
    missed: list[HarvestItem] = []
    agenda = [
        AgendaDay(day=today + timedelta(days=i), is_today=(i == 0))
        for i in range(AGENDA_DAYS)
    ]

    for p in plantings:
        start, end = p.window_start, p.window_end
        if end < today:
            if p.harvest_count == 0:
                missed.append(HarvestItem(p, "missed", start, end, (today - end).days, 0))
            continue
        if start <= today:
            opened.append(HarvestItem(p, "open", start, end, (end - today).days, p.harvest_count))
        else:
            soon.append(
                HarvestItem(
                    p, "soon", start, end, (start - today).days, p.harvest_count,
                    is_imminent=(start - today).days <= lead_days,
                )
            )
        for cell in agenda:
            if start <= cell.day <= end:
                cell.crops.append(f"{p.crop.crop_name} ({p.field.field_name})")

    # Most overdue first for missed windows; soonest first elsewhere.
    missed.sort(key=lambda item: -item.days)
    return HarvestSection(opened, soon, missed, agenda)

def _money_sum(queryset, expression):
    value = queryset.aggregate(total=Sum(expression))["total"]
    return value or Decimal("0.00")


def sales_section(today: date, include_payments: bool) -> SalesSection:
    """Month-to-date sales and, if permitted, what is still owed."""
    month_start = today.replace(day=1)
    line_total = ExpressionWrapper(F("quantity") * F("unit_price"), output_field=MONEY)
    month_sales = _money_sum(
        OrderItem.objects.filter(order__order_date__gte=month_start, order__order_date__lte=today),
        line_total,
    )
    section = SalesSection(
        month_label=today.strftime("%B %Y"),
        month_sales=month_sales,
        show_payments=include_payments,
    )
    if not include_payments:
        return section

    section.collected_this_month = _money_sum(
        Payment.objects.filter(payment_date__gte=month_start, payment_date__lte=today),
        F("amount_paid"),
    )
    unpaid = Order.objects.with_outstanding_balance()
    totals = unpaid.aggregate(total=Sum("annotated_balance"), count=Count("pk"))
    section.outstanding_total = totals["total"] or Decimal("0.00")
    section.unpaid_count = totals["count"] or 0
    if section.unpaid_count:
        orders = list(
            unpaid.select_related("customer")
            .order_by("order_date", "pk")[:UNPAID_LIST_LIMIT]
        )
        for order in orders:
            order.days_outstanding = max((today - order.order_date).days, 0)
        section.unpaid_orders = orders
    return section


def build_dashboard(user) -> dict:
    """Assemble only the sections ``user`` is allowed to see."""
    today = timezone.localdate()
    context: dict = {"today": today, "harvests": None, "sales": None}
    if can_see_harvests(user):
        context["harvests"] = harvest_section(today)
    if can_see_sales(user):
        context["sales"] = sales_section(today, include_payments=user.has_perm("sales.view_payment"))

    attention = 0
    if context["harvests"]:
        attention += context["harvests"].attention_count
    if context["sales"] and context["sales"].show_payments:
        attention += context["sales"].unpaid_count
    context["attention_count"] = attention
    return context