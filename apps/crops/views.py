"""Permission-checked CRUD views for crops, fields, and planting records."""

from collections import Counter, defaultdict
from datetime import timedelta
from decimal import Decimal
from hashlib import sha256

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Prefetch, Q
from django.http import HttpResponseBadRequest
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    TemplateView,
    UpdateView,
)
from django.views.generic.list import ListView

from apps.harvests.models import Harvest
from apps.accounts.permissions import ApplicationRoleRequiredMixin

from config.view_mixins import ProtectedDeleteMixin

from .forms import CropForm, FieldForm, PlantingForm
from .models import Crop, Field, Planting


FIELD_BOARD_CROP_COLORS = (
    "#477b55",
    "#9b6a37",
    "#5d7890",
    "#8a648d",
    "#71813c",
    "#b66a52",
)


def _field_board_crop_color(crop_name):
    """Choose a stable board color without storing presentation data."""
    color_index = sha256(crop_name.casefold().encode("utf-8")).digest()[0]
    return FIELD_BOARD_CROP_COLORS[color_index % len(FIELD_BOARD_CROP_COLORS)]


class FieldBoardView(
    LoginRequiredMixin,
    ApplicationRoleRequiredMixin,
    PermissionRequiredMixin,
    TemplateView,
):
    """Show field plantings and their derived harvest status on one timeline."""

    permission_required = (
        "crops.view_planting",
        "crops.view_crop",
        "crops.view_field",
        "harvests.view_harvest",
    )
    template_name = "crops/field_board.html"

    def get(self, request, *args, **kwargs):
        weeks = request.GET.get("weeks", "14")
        crop_id = request.GET.get("crop", "")
        search_query = request.GET.get("q", "").strip()
        view_mode = request.GET.get("view", "timeline")

        if weeks not in {"8", "14", "26"}:
            return HttpResponseBadRequest("Choose a supported timeline range.")
        if crop_id and (
            not crop_id.isascii()
            or not crop_id.isdecimal()
            or len(crop_id) > 10
            or not Crop.objects.filter(pk=int(crop_id)).exists()
        ):
            return HttpResponseBadRequest("Choose an existing crop.")
        if len(search_query) > 100:
            return HttpResponseBadRequest("Search text must be 100 characters or fewer.")
        if view_mode not in {"timeline", "all"}:
            return HttpResponseBadRequest("Choose a supported planting view.")

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        weeks = int(self.request.GET.get("weeks", "14"))
        crop_id = self.request.GET.get("crop", "")
        search_query = self.request.GET.get("q", "").strip()
        view_mode = self.request.GET.get("view", "timeline")

        plantings = (
            Planting.objects.select_related("crop", "field")
            .prefetch_related(
                Prefetch(
                    "harvests",
                    queryset=Harvest.objects.order_by("harvesting_date", "pk"),
                )
            )
            .order_by("field__field_name", "planting_date", "pk")
        )
        if crop_id:
            plantings = plantings.filter(crop_id=int(crop_id))
        if search_query:
            plantings = plantings.filter(
                Q(crop__crop_name__icontains=search_query)
                | Q(field__field_name__icontains=search_query)
            )

        all_items = []
        plantings_by_field = defaultdict(list)
        needs_picking = []
        crop_counts = Counter()
        activity_counts = [0] * 8
        activity_start = today - timedelta(days=today.weekday() + 49)
        production_field_ids = set()
        timeline_days = weeks * 7

        for planting in plantings:
            status = planting.status
            harvests = list(planting.harvests.all())
            totals_by_unit = defaultdict(lambda: Decimal("0"))
            for harvest in harvests:
                totals_by_unit[harvest.unit] += harvest.quantity_harvested
                week_index = (harvest.harvesting_date - activity_start).days // 7
                if 0 <= week_index < len(activity_counts):
                    activity_counts[week_index] += 1

            totals = [
                {"unit": unit, "quantity": quantity}
                for unit, quantity in sorted(totals_by_unit.items())
            ]
            color = _field_board_crop_color(planting.crop.crop_name)
            days_until_start = (planting.harvest_start - today).days
            if status == "soon":
                day_indicator = f"Opens in {days_until_start} days"
            elif status in {"ready", "partial"}:
                day_in_window = (today - planting.harvest_start).days + 1
                day_indicator = f"Day {day_in_window} of 3"
            elif status == "missed":
                days_overdue = (today - planting.harvest_end).days
                day_indicator = (
                    f"Missed {days_overdue} day"
                    f"{'s' if days_overdue != 1 else ''} ago"
                )
            elif status == "done":
                day_indicator = "Window closed"
            elif any(
                harvest.harvesting_date < planting.harvest_start
                for harvest in harvests
            ):
                day_indicator = "Harvest recorded before window"
            else:
                day_indicator = f"Opens in {days_until_start} days"

            window_position = min(100, max(0, days_until_start / timeline_days * 100))
            growth_start_days = max(0, (planting.planting_date - today).days)
            growth_width_days = max(0, days_until_start - growth_start_days)
            growth_start = min(100, growth_start_days / timeline_days * 100)
            growth_width = min(
                max(0, 100 - growth_start),
                growth_width_days / timeline_days * 100,
            )
            harvest_events = []
            for harvest in harvests:
                event_days = (harvest.harvesting_date - today).days
                event_position = min(100, max(0, event_days / timeline_days * 100))
                harvest_events.append({
                    "harvest": harvest,
                    "timeline_position": event_position,
                })

            status_label = {
                "growing": "Growing",
                "soon": "Opening soon",
                "ready": "Open",
                "partial": "Part-harvested",
                "missed": "Missed",
                "done": "Closed",
            }[status]
            recorded_volume = ", ".join(
                f"{total['quantity']} {total['unit']}" for total in totals
            ) or "none recorded"
            item = {
                "planting": planting,
                "status": status,
                "status_label": status_label,
                "day_indicator": day_indicator,
                "crop_color": color,
                "totals_by_unit": totals,
                "harvest_events": harvest_events,
                "window_position": window_position,
                "growth_start": growth_start,
                "growth_width": growth_width,
                "accessible_label": (
                    f"{planting.crop.crop_name} in {planting.field.field_name}; "
                    f"{status_label}; planted {planting.planting_date}; "
                    f"expected harvest window {planting.harvest_start} to "
                    f"{planting.harvest_end}; maturity "
                    f"{planting.crop.maturity_days} days; recorded volume "
                    f"{recorded_volume}."
                ),
            }
            all_items.append(item)
            if status != "done":
                production_field_ids.add(planting.field_id)
                crop_counts[planting.crop_id] += 1
            if status in {"ready", "partial", "soon", "missed"}:
                needs_picking.append(item)

        visible_items = [
            item
            for item in all_items
            if view_mode == "all" or item["status"] != "done"
        ]
        visible_by_field = defaultdict(list)
        for item in visible_items:
            visible_by_field[item["planting"].field_id].append(item)

        fields = Field.objects.order_by("field_name", "pk")
        field_rows = [
            {"field": field, "plantings": visible_by_field[field.pk]}
            for field in fields
        ]

        active_crop_items = [
            item for item in all_items if item["status"] != "done"
        ]
        active_crop_count = sum(crop_counts.values())
        crop_segments = []
        gradient_segments = []
        accumulated_percent = 0.0
        crops_by_id = {
            item["planting"].crop_id: item["planting"].crop
            for item in active_crop_items
        }
        for crop_id_key, count in sorted(
            crop_counts.items(),
            key=lambda entry: crops_by_id[entry[0]].crop_name.casefold(),
        ):
            crop = crops_by_id[crop_id_key]
            end_percent = accumulated_percent + count / active_crop_count * 100
            color = _field_board_crop_color(crop.crop_name)
            crop_segments.append({
                "crop": crop,
                "count": count,
                "color": color,
            })
            gradient_segments.append(
                f"{color} {accumulated_percent:.2f}% {end_percent:.2f}%"
            )
            accumulated_percent = end_percent

        maximum_activity = max(activity_counts, default=0) or 1
        activity_weeks = []
        for week_index, count in enumerate(activity_counts):
            week_start = activity_start + timedelta(days=week_index * 7)
            activity_weeks.append({
                "start": week_start,
                "count": count,
                "height_percent": count / maximum_activity * 100,
            })

        axis_labels = []
        for step in range(5):
            offset_days = round(timeline_days * step / 4)
            axis_labels.append({
                "position": step * 25,
                "date": today + timedelta(days=offset_days),
                "is_today": step == 0,
            })

        needs_picking.sort(
            key=lambda item: (
                item["planting"].harvest_start,
                item["planting"].field.field_name.casefold(),
            )
        )
        context.update({
            "field_rows": field_rows,
            "planting_count": len(all_items),
            "field_count": len(production_field_ids),
            "active_planting_count": active_crop_count,
            "open_window_count": sum(
                item["status"] in {"ready", "partial"} for item in all_items
            ),
            "opening_soon_count": sum(
                item["status"] == "soon" for item in all_items
            ),
            "missed_window_count": sum(
                item["status"] == "missed" for item in all_items
            ),
            "needs_picking": needs_picking,
            "crop_segments": crop_segments,
            "crop_donut_style": (
                f"conic-gradient({', '.join(gradient_segments)})"
                if gradient_segments
                else ""
            ),
            "activity_weeks": activity_weeks,
            "axis_labels": axis_labels,
            "crop_options": Crop.objects.order_by("crop_name"),
            "selected_crop": crop_id,
            "search_query": search_query,
            "selected_weeks": str(weeks),
            "view_mode": view_mode,
            "filter_active": bool(crop_id or search_query),
            "today": today,
        })
        return context


class CropsOverviewView(PermissionRequiredMixin, TemplateView):
    """Show catalogue counts and the most recently created plantings."""

    permission_required = (
        "crops.view_crop",
        "crops.view_field",
        "crops.view_planting",
    )
    template_name = "crops/overview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "crop_count": Crop.objects.count(),
            "field_count": Field.objects.count(),
            "planting_count": Planting.objects.count(),
            "recent_plantings": (
                Planting.objects.select_related("crop", "field")
                .order_by("-planting_date", "-pk")[:5]
            ),
        })
        return context


class CropListView(PermissionRequiredMixin, ListView):
    permission_required = ("crops.view_crop", "crops.view_planting")
    model = Crop
    template_name = "crops/crop_list.html"
    context_object_name = "crops"
    queryset = Crop.objects.annotate(
        planting_count=Count("plantings")
    ).order_by("crop_name", "pk")


class CropDetailView(PermissionRequiredMixin, DetailView):
    permission_required = (
        "crops.view_crop",
        "crops.view_planting",
        "crops.view_field",
    )
    model = Crop
    template_name = "crops/crop_detail.html"
    context_object_name = "crop"

    def get_queryset(self):
        return Crop.objects.prefetch_related(
            Prefetch(
                "plantings",
                queryset=Planting.objects.select_related("field").order_by("-planting_date", "-pk"),
            )
        )


class FieldListView(PermissionRequiredMixin, ListView):
    permission_required = ("crops.view_field", "crops.view_planting")
    model = Field
    template_name = "crops/field_list.html"
    context_object_name = "fields"
    queryset = Field.objects.annotate(
        planting_count=Count("plantings")
    ).order_by("field_name", "pk")


class FieldDetailView(PermissionRequiredMixin, DetailView):
    permission_required = (
        "crops.view_field",
        "crops.view_planting",
        "crops.view_crop",
    )
    model = Field
    template_name = "crops/field_detail.html"
    context_object_name = "field"

    def get_queryset(self):
        return Field.objects.prefetch_related(
            Prefetch(
                "plantings",
                queryset=Planting.objects.select_related("crop").order_by("-planting_date", "-pk"),
            )
        )


class ProtectedDeleteView(PermissionRequiredMixin, ProtectedDeleteMixin, DeleteView):
    """Combine model permissions with the shared protected-delete behavior."""

    blocked_message = "This record is in use and cannot be deleted."


class CropCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = "crops.add_crop"
    model = Crop
    form_class = CropForm
    template_name = "crops/crop_form.html"
    success_url = reverse_lazy("crops:crop-list")
    success_message = "Crop created."


class CropUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = ("crops.change_crop", "crops.view_planting")
    model = Crop
    form_class = CropForm
    template_name = "crops/crop_form.html"
    context_object_name = "crop"
    success_url = reverse_lazy("crops:crop-list")
    success_message = "Crop updated."


class CropDeleteView(ProtectedDeleteView):
    """Prevent removing crops referenced by plantings or historic sales."""

    permission_required = "crops.delete_crop"
    model = Crop
    template_name = "crops/crop_confirm_delete.html"
    context_object_name = "crop"
    success_url = reverse_lazy("crops:crop-list")
    deleted_message = "Crop deleted."
    blocked_message = "This crop has plantings or sales and cannot be deleted."

    def is_deletion_blocked(self):
        return (
            self.object.plantings.exists()
            or self.object.order_items.exists()
        )


class FieldCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = "crops.add_field"
    model = Field
    form_class = FieldForm
    template_name = "crops/field_form.html"
    success_url = reverse_lazy("crops:field-list")
    success_message = "Field created."


class FieldUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = ("crops.change_field", "crops.view_planting")
    model = Field
    form_class = FieldForm
    template_name = "crops/field_form.html"
    context_object_name = "field"
    success_url = reverse_lazy("crops:field-list")
    success_message = "Field updated."


class FieldDeleteView(ProtectedDeleteView):
    """Prevent removing a field that still has planting records."""

    permission_required = "crops.delete_field"
    model = Field
    template_name = "crops/field_confirm_delete.html"
    context_object_name = "field"
    success_url = reverse_lazy("crops:field-list")
    deleted_message = "Field deleted."
    blocked_message = "This field has plantings and cannot be deleted."

    def is_deletion_blocked(self):
        return self.object.plantings.exists()


class PlantingListView(PermissionRequiredMixin, ListView):
    permission_required = (
        "crops.view_planting",
        "crops.view_crop",
        "crops.view_field",
    )
    model = Planting
    template_name = "crops/planting_list.html"
    context_object_name = "plantings"

    def get_queryset(self):
        return (
            Planting.objects
            .select_related("crop", "field")
            .order_by("-planting_date", "-pk")
        )


class PlantingDetailView(PermissionRequiredMixin, DetailView):
    """Show a planting with its crop, field, and recorded harvests."""

    permission_required = (
        "crops.view_planting",
        "crops.view_crop",
        "crops.view_field",
        "harvests.view_harvest",
    )
    model = Planting
    template_name = "crops/planting_detail.html"
    context_object_name = "planting"

    def get_queryset(self):
        return (
            Planting.objects
            .select_related("crop", "field")
            .prefetch_related(
                Prefetch(
                    "harvests",
                    queryset=Harvest.objects.order_by("-harvesting_date", "-pk"),
                )
            )
        )


class PlantingCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = ("crops.add_planting", "crops.view_crop", "crops.view_field")
    model = Planting
    form_class = PlantingForm
    template_name = "crops/planting_form.html"
    success_url = reverse_lazy("crops:planting-list")
    success_message = "Planting created."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["has_crops"] = Crop.objects.exists()
        context["has_fields"] = Field.objects.exists()
        return context


class PlantingUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = (
        "crops.change_planting",
        "crops.view_crop",
        "crops.view_field",
    )
    model = Planting
    form_class = PlantingForm
    template_name = "crops/planting_form.html"
    context_object_name = "planting"
    success_url = reverse_lazy("crops:planting-list")
    success_message = "Planting updated."


class PlantingDeleteView(ProtectedDeleteView):
    """Prevent removing a planting that already has harvest history."""

    permission_required = "crops.delete_planting"
    model = Planting
    template_name = "crops/planting_confirm_delete.html"
    context_object_name = "planting"
    success_url = reverse_lazy("crops:planting-list")
    deleted_message = "Planting deleted."
    blocked_message = "This planting has harvest records and cannot be deleted."

    def is_deletion_blocked(self):
        return self.object.harvests.exists()
