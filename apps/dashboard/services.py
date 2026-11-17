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

from django.conf import settings
from django.db.models import Count

from apps.crops.models import Planting

# How far ahead the harvest agenda looks, and how far back a "nothing recorded"
# window is still worth nagging about (older ones are history, not tasks).
AGENDA_DAYS = 14
MISSED_LOOKBACK_DAYS = 30


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