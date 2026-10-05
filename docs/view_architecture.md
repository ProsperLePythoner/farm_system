# View Architecture and Workflows

This document separates existing application behavior from planned workflows.
The diagrams describe user-facing intent; role-specific authorization and
dashboards are not yet implemented.

## Current URL structure

The project mounts app URLs under these prefixes:

```text
/dashboard/    dashboard
/crops/        crop/planting workflows
/harvests/     harvest workflows
/customers/    customer CRUD and order history
/sales/        order CRUD with harvest-linked line items
/accounts/     account app
/admin/        Django admin
```

### Implemented user-facing workflows

Planting pages are served under `/crops/plantings/`:

| User task | Route pattern | View |
|---|---|---|
| List plantings | `plantings/` | `ListView` |
| Create a planting | `plantings/new/` | `CreateView` |
| View a planting and its harvests | `plantings/<pk>/` | `DetailView` |
| Edit a planting | `plantings/<pk>/edit/` | `UpdateView` |
| Delete a planting | `plantings/<pk>/delete/` | `DeleteView` |

Harvest pages are served under `/harvests/`:

| User task | Route pattern | View |
|---|---|---|
| List harvests | `/` (app root) | `ListView` |
| Record a harvest for a planting | `plantings/<planting_pk>/new/` | `CreateView` |
| Edit a harvest | `<pk>/edit/` | `UpdateView` |
| Delete a harvest | `<pk>/delete/` | `DeleteView` |

The harvest list displays both recorded `Harvest` rows and upcoming windows
derived from `Planting` dates and crop maturity days. Each upcoming planting
links to the context-aware record form for that specific planting. At this
stage, upcoming means that the calculated harvest start is today or later;
status categories and the handling of past-due plantings remain to be defined.

Recording a harvest from its planting provides context: the planting, crop, and
field are known, while the user supplies the harvest date, quantity, and notes.
The form and view enforce the relationship and snapshot the crop's current unit.

Customer pages are served under `/customers/`:

| User task | Route pattern | View |
|---|---|---|
| List customers | `/` (app root) | `ListView` |
| Add a customer | `new/` | `CreateView` |
| View contact details and order history | `<pk>/` | `DetailView` |
| Edit a customer | `<pk>/edit/` | `UpdateView` |
| Delete a customer without orders | `<pk>/delete/` | `DeleteView` |

Customer deletion is blocked when orders exist, preserving customer references
and order history. Customer search and filtering are not implemented yet.

Sales order pages are served under `/sales/`:

| User task | Route pattern | View |
|---|---|---|
| List orders | `/` (app root) | `ListView` |
| Create an order with harvest-linked items | `orders/new/` | `CreateView` |
| View order items and calculated summary | `orders/<pk>/` | `DetailView` |
| Edit an order and its items | `orders/<pk>/edit/` | `UpdateView` |
| Delete an order without payment history | `orders/<pk>/delete/` | `DeleteView` |

New order items select a harvest and snapshot its crop and unit. Legacy items
recorded against a crop only are preserved and remain visible. Payment forms
and stock availability enforcement are not implemented yet.

### Incomplete routes

- The dashboard view currently renders the shared base template; it is not yet
  a data-driven or role-specific dashboard.
- There is no complete sign-in, role, or permission workflow documented by the
  current views.

## Intended production workflow

```text
Maintain crop and field records
              │
              ▼
       Create a planting
              │
              ▼
     Monitor expected window
              │
              ▼
       Record each harvest
              │
              ▼
      Review planting history
```

Each harvest belongs to one planting. A planting may have multiple harvest
records. Recording a harvest does not currently create a separate inventory
batch or directly affect an order.

## Sales workflow (partially implemented)

```text
Select customer → Create order → Add harvest-linked items → Record payment(s)
```

Order creation and harvest-linked items are implemented. Payments remain
separate from orders to support installments, but payment entry and stock
reservation/deduction workflows are still pending.

## Future role-specific experience

The following roles and dashboards are product goals, not current access-control
rules:

- **Farm manager:** plantings, expected harvests, harvest history, fields.
- **Sales clerk:** customers, orders, payments, outstanding balances.
- **Administrator:** user and system administration, with appropriate access.

Use Django groups/permissions or another explicit authorization strategy before
exposing role-specific data in a multi-user deployment. A dashboard should be
built from verified data and business rules rather than acting as a separate
source of truth.
