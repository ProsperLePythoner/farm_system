# Field Board — UI intent and implementation brief

**Project:** Agribusiness Management System (`farm_system`)
**Date:** 2026-11-02
**Status:** Proposal, not yet implemented. No files under `apps/`, `templates/`, `static/` or `config/` have been modified by this work.
**Visual reference:** `field-board-v2.html` in the chat-session visualizations folder (interactive mockup, sample data).

This document states what I intend to achieve on the frontend, why, and how far I intend to go. It is written to be compared line-by-line against another agent's proposal, so it names files, quotes existing constraints, and records the decisions I rejected.

---

## 1. Problem statement

The application is functionally a correct Django CRUD layer over a real domain pipeline
(`Field → Planting → Harvest → OrderItem → Order → Payment`), but its interface is shaped like
the database rather than like farm work.

Evidence, all verified in the current checkout:

| # | Finding | Where |
|---|---|---|
| 1 | The dashboard renders no operational data at all — it is a `TemplateView` with no `get_context_data`, i.e. a permission-gated link page. | `apps/dashboard/views.py:9-12` |
| 2 | `README.md` already promises the dashboard surfaces upcoming harvests, available stock, outstanding balances and recent orders. That promise is unmet. | `README.md:66`, `README.md:279-288` |
| 3 | Crops, Fields, Plantings and Harvests are four separate list pages. Nothing shows a planting in time or in relation to its field. | `docs/visual_layout.md:33-42` |
| 4 | The most valuable derived fact in the system — the 3-day harvest window — exists only as a Python property and a plain list. | `apps/crops/models.py:136-157` |
| 5 | No user-facing list has search, filtering, sorting or pagination. `Paginator` appears nowhere in the project; `search_fields` exist only in Django admin. | `apps/*/admin.py`, absence across `apps/*/views.py` |
| 6 | Forms render as raw `{{ form.as_p }}`, so browser-default widgets sit inside an otherwise styled shell. | 8 templates incl. login, crop, field, customer, harvest, order, user, profile |
| 7 | `<table>`, page-header and action-button markup is duplicated across ~20 templates; the only shared "component" is `templates/base/icon.html`. | `templates/**` |
| 8 | `Payment` rows are displayed but cannot be created — no form, view or route. Outstanding balance is computed and then dead-ends. | `DOCS_NOTES.md:28-32` |
| 9 | `docs/visual_layout.md:55-57` already states the correct principle: "Navigation should mirror business tasks rather than expose database tables directly." The nav currently does the opposite. | `docs/visual_layout.md:55-57` |

The single highest-value gap is #3 + #4: a farm operator's question is *"what is ready, where, and when"* — and the app cannot answer it in one screen.

---

## 2. Intent

Build one new screen — the **Field Board** — that replaces the mental model of four CRUD lists
with a season timeline: one row per field, one bar per planting, and an explicit marker for each
harvest window, with derived status (growing / open / part-harvested / missed / closed).

Then, and only then, spend effort on the shared layer that makes further screens cheaper:
extracted partials, styled form rendering, and list ergonomics.

Success criteria — each is checkable:

1. A Farm Manager can see every open harvest window on one screen without clicking into a detail page.
2. A missed window is visually unmistakable and reachable in one action from the existing harvest-record route.
3. No new database column, no migration, and no change to any business rule. All state is derived from `planting_date`, `crop.maturity_days`, and the presence of `Harvest` rows.
4. The screen renders server-side with Django templates; JavaScript is used only for filtering, tooltips and the detail drawer, and the page is still usable with JS disabled.
5. The forest-green identity, Inter, and the self-hosted Material Symbols subset are preserved and used correctly.

---

## 3. Constraints I am honoring (and where they come from)

These are not my preferences; they are already written down in this repo.

| Constraint | Source |
|---|---|
| No React, Tailwind, Bootstrap or another frontend framework | `docs/ui_polish.md:199`, `README.md:133` |
| No theme switching | `docs/ui_polish.md:200` |
| Preserve the forest-green identity and the existing shell | `docs/ui_polish.md:17`, `docs/ui_polish.md:161` |
| Inter and Material Symbols stay self-hosted; no runtime Google Fonts request | `docs/ui_polish.md:71,88` |
| Icons must use the local subset only — 17 glyphs: `add, agriculture, dashboard, delete, edit, event_available, grass, landscape, lock, lock_open, logout, manage_accounts, menu, people, person_add, point_of_sale, space_dashboard` | `static/fonts/material-symbols/icons.txt` |
| Store facts, calculate results; do not duplicate derived data | `README.md:460-475` |
| Server-side permission enforcement, not just hidden links | `README.md:163` |
| Keep V1 focused; defer features without a demonstrated need | `README.md:477-483` |

Anything in this brief that appears to violate these is a mistake in the brief, and should be scored against it.

---

## 4. Information architecture change

Before: `Dashboard · Overview · Crops · Fields · Plantings · Harvests · Customers · Sales` — table names.

After (production group only):

```
Dashboard                      ← operational summary (later phase)
Production
  Field Board                  ← NEW default landing for production roles
  Plantings                    ← keeps full CRUD + search/filter/pagination
  Harvests                     ← record/edit, grouped by planting
  Crops & Fields               ← reference data, merged into one page
Customers
Sales
```

`Crops`, `Fields` and `Plantings` do not disappear; they stop being the primary way to work.
The Board is a view over `Planting`, not a new entity.

---

## 5. Screen specification — Field Board

### 5.1 Regions

| Region | Content | Source of truth |
|---|---|---|
| Page header | Title, planting count, Timeline / All-plantings toggle, `+ New planting` | — |
| Stat strip (4) | Acres in production · windows open now · opening within 7 days · missed windows | derived in the view |
| Timeline (primary) | One row per `Field`; one bar per `Planting` from `planting_date` → `harvest_start`; a marker cap for the window; dots for recorded `Harvest` events | `Planting`, `Harvest` |
| "Needs picking" card | Open, imminent and missed windows, each with a day-of-window indicator and a one-click record action | `Planting.is_ready_for_harvest` + `Harvest` |
| "Plantings by crop" card | Donut of active plantings per crop; doubles as the crop filter | `Planting` |
| "Harvest activity" card | Count of harvest events per week | `Harvest.harvesting_date` |
| Detail drawer | All planting facts, its harvest events, actions | `Planting`, `Harvest` |

### 5.2 The two geometry decisions that matter

1. **The window is a marker, not a bar.** `harvest_end = harvest_start + 2` (`apps/crops/models.py:150-157`), so a 3-day window spans roughly 2 px at a 14-week scale. Drawing it as a proportional block requires lying about its width. It is drawn as a fixed-size cap at the end of the bar, with the 3 days expressed as three dots in the detail card.
2. **Quantities are never summed across crops.** `Harvest.unit` is copied per record and crop units range over `g, kg, tonne, bag, crate, bunch, heads, pcs` (`apps/crops/models.py:55-63`). A single "total harvested" KPI would be arithmetically false. Volumes stay grouped by unit; the activity chart counts events, not mass.

### 5.3 Derived status (no new model field)

```
done      harvest rows exist AND today > harvest_end
partial   harvest rows exist AND harvest_start <= today <= harvest_end
missed    no harvest rows      AND today > harvest_end
ready     no harvest rows      AND harvest_start <= today <= harvest_end
soon      no harvest rows      AND 0 < harvest_start - today <= 7 days
growing   otherwise
```

`missed` is the state the current UI cannot express and the one that costs real money.

---

## 6. Visual system contract

Values are the ones in the accepted mockup; another proposal can be compared numerically against them.

| Token | Value | Note |
|---|---|---|
| `--color-bg` | `#f2f6f3` | current `#f3f6f4` (`base.css:8`) kept within a hair |
| `--color-forest` / `-deep` | `#165a34` / `#0f3f24` | unchanged (`base.css:10-11`) |
| `--ink` / `--ink-2` / `--ink-3` | `#15231b` / `#4b5c53` / `#7d8c84` | replaces one flat `--color-text` |
| `--mint` / `--mint-soft` | `#e7f2e9` / `#f1f7f2` | matches existing active-nav fill (`base.css:294-300`) |
| status: growing / open / missed / recorded | `#4c9a5b` / `#d98a1f` / `#c4553e` / `#3f83a8` | new, four states only |
| radius: card / control / pill | `20px` / `12px` / `999px` | current is 6–8px throughout (`base.css:283,412`) |
| shadow | `0 2px 4px rgba(16,40,26,.04), 0 14px 30px -18px rgba(16,60,35,.28)` | replaces hairline borders as the primary separation device |
| type | Inter 400–700 variable, `font-variant-numeric: tabular-nums` on all figures | h1 27px/700, card title 16.5px, body 15px, label 11px/700/.1em uppercase |
| icon class | reuse `.material-symbols-outlined` verbatim (`base.css:325-342`) | no per-icon styling |
| grid | sidebar 250px (current 248), content max-width 1200px (unchanged, `base.css:368`) | no shell reflow |

Deliberately **not** used: 1px borders on every card, gradient-filled bars, all-caps micro-labels inside data bars, colored top-border stat tiles. Those are the tells of a generic admin template and were the specific failure of the first mockup.

---

## 7. Data and computation contract

- The view supplies a list of plain dicts (or a light dataclass), computed once:
  `field, crop, planting_date, harvest_start, harvest_end, status, days_remaining, harvests[], total_by_unit`.
- Query shape: `Planting.objects.select_related("crop","field").prefetch_related("harvests")`,
  ordered by `field.field_name, planting_date`. No N+1 on harvests.
- Window arithmetic stays in `Planting` (`apps/crops/models.py:136-157`). The view does not reimplement `+2 days`.
- Status derivation lives in one place — a `Planting.status` property or a small `apps/crops/services.py` — so the Board, the dashboard and any future reminder feature agree.
- Timezone: `Africa/Dar_es_Salaam` via `timezone.localdate()`, never `date.today()`.
- Permissions: `LoginRequiredMixin` + `ApplicationRoleRequiredMixin` and `perms.crops.view_planting` gating per link, exactly as `templates/base/sidebar.html` already does.

---

## 8. Interaction specification

| Interaction | Behavior | Without JS |
|---|---|---|
| Crop filter / zoom 8-14-26 wk / search | GET query params, re-rendered server-side, enhanced by JS | plain `<a>` query links still work |
| Bar or marker click | detail drawer opens | full planting detail page still exists |
| `Record harvest` | links to existing `harvests:harvest-create` (`/harvests/plantings/<pk>/new/`) | unchanged |
| Keyboard | every bar is a real `<button>`, arrow-navigable, visible focus ring, `Esc` closes drawer | native |
| Empty state | field row reads "no active plantings"; board with zero plantings offers one primary action | — |
| Missed window | clay marker + soft pulse; pulse is disabled under `prefers-reduced-motion` | color + text label still convey it |
| Tooltip | dates, maturity, recorded volume with unit | bar `aria-label` carries the same facts |

---

## 9. Implementation plan

| Phase | Deliverable | Files touched | Risk |
|---|---|---|---|
| 0 | Token layer: add ink/status/radius/shadow variables, keep existing names working | `static/css/base.css` (additive) | low |
| 1 | `Planting.status` + summary helpers, unit-tested | `apps/crops/models.py`, `apps/crops/tests.py` | low |
| 2 | Board view + template + URL + nav entry | `apps/crops/views.py`, `apps/crops/urls.py`, `templates/crops/field_board.html`, `templates/base/sidebar.html` | medium — nav/permission edits |
| 3 | Shared partials: `table.html`, `page_header.html`, `form_field.html`, `empty_state.html`; kill `{{ form.as_p }}` | `templates/base/partials/*`, ~20 templates | medium — bulk diff |
| 4 | List ergonomics: search + filter + sort + `Paginator` on planting/harvest/order/customer lists | `apps/*/views.py`, list templates | medium |
| 5 | Dashboard becomes the operational summary, reusing Phase 1 helpers | `apps/dashboard/views.py`, `templates/dashboard/dashboard.html` | low |
| 6 | Progressive enhancement JS: filter, zoom, drawer | `static/js/field_board.js` | low |

Phases 1–2 are the "did it work" test. Phases 3–4 are the foundation that makes the remaining screens consistent. Nothing here requires a migration.

Note on `static/`: `DOCS_NOTES.md:71-73` records a standing instruction not to edit `static/`. Phase 0 needs `base.css`. I will not touch it until that instruction is confirmed or lifted — flagging it rather than silently expanding scope, as `docs/ui_polish.md:203` requires.

---

## 10. Out of scope (explicitly)

- Livestock, equipment, workers, inventory, expenses — no models exist; inventing UI for them would be fiction.
- Weather, satellite imagery, maps — no data source, and image generation is unavailable on this plan.
- Payment entry UI — a real gap (`DOCS_NOTES.md:28-32`), but it needs business rules first: overpayment handling and correction behavior are undefined (`DOCS_NOTES.md:84-87`). UI before rules would bake in the wrong answer.
- Email/SMS reminders, calendar feature, mobile app — `README.md:323-337` defers these; `docs/ui_polish.md:200` excludes them.
- Repo hygiene items I noticed but will not bundle into a UI change: dead `django-tailwind`/`pytailwindcss` deps with an empty `theme/` app, the leftover `testing` app with a debug `print`, the empty `static/js/dashboard.js`, and `?v=` query-string cache busting.

---

## 11. Decisions I need from you

1. **Is `docs/images/farm-management-dashboard.png` actually your taste target?** The whole visual contract in §6 is derived from it. If it is not, name a product whose UI you like and §6 gets rewritten before any code.
2. **Where does the Board live?** `/crops/board/` (my default, least disruptive) vs. making it the production landing page.
3. **Per-crop color.** There is no color field on `Crop`. Options: (a) add `Crop.color` `CharField` — one migration; (b) hash the crop name against a fixed palette — no migration, colors shift as crops are added; (c) drop color and use tint only. I recommend (b) for now, (a) if you want control.
4. **Acreage per planting.** `Field.field_size` is per field, so a field with two plantings cannot report "acres planted" honestly. Either accept "fields in production" as the metric, or add `Planting.area_ac` (migration + form field). I recommend accepting the weaker metric until it bites.
5. **Phase 0 permission** to edit `static/css/base.css` (see §9 note).

---

## 12. What I rejected, and why — for comparison

| Tempting proposal | Verdict | Reason |
|---|---|---|
| Rewrite the frontend as React/Next + API | Rejected | Violates `docs/ui_polish.md:199` and `README.md:133`; would rebuild working CRUD for no domain gain |
| Finish the Tailwind integration | Rejected | Deps are already present but unused; a build pipeline for one stylesheet of 952 lines is not a demonstrated need |
| Chart.js for the timeline | Rejected | A chart library cannot express field-relative rows; hand-rolled CSS/SVG is smaller and matches the shell |
| Theme switching / dark mode | Rejected | Excluded by `docs/ui_polish.md:200`. My first mockup included it — that was a scope violation, not a feature |
| Kanban "planting stages" board | Rejected | There is no status field on `Planting`; a Kanban would require storing state the system already derives |
| KPI "total harvested (kg)" | Rejected | Arithmetically invalid across units (§5.2) |
| Adding a `HarvestWindow` model | Rejected | Duplicates derived data, against `README.md:460-475` |

---

## 13. Rubric for comparing two approaches

Score each proposal against these, in this order:

1. **Constraint compliance** — does it respect the repo's own written rules (`docs/ui_polish.md`, `README.md` design philosophy)?
2. **Groundedness** — are claims backed by real files, models and line references, or is it generic dashboard advice?
3. **Domain fit** — does it answer *what is ready, where, when* for a crop-to-sales farm in Tsh, or does it impose SaaS conventions?
4. **Data honesty** — does it refuse to display numbers the schema cannot support?
5. **Blast radius** — migrations, new dependencies, build steps, rewrites. Fewer is better.
6. **Reversibility** — can each phase ship alone and be backed out?
7. **Craft** — does the visual proposal use the project's own identity, or a template's?
8. **Stated non-goals** — a proposal that does not say what it will *not* do has not decided anything.
