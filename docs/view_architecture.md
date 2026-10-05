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
/customers/    customer app (routes not implemented)
/sales/        placeholder order list/detail responses
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

Recording a harvest from its planting provides context: the planting, crop, and
field are known, while the user supplies the harvest date, quantity, and notes.
The form and view enforce the relationship and snapshot the crop's current unit.

### Incomplete routes

- `/sales/` and `/sales/<pk>/` currently return placeholder responses.
- Customer URLs are not yet defined.
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

## Intended sales workflow (not implemented)

```text
Select customer → Create order → Add crop items → Record payment(s)
```

Payments are separate from orders to allow installments. Before completing this
workflow, define order lifecycle and stock reservation/deduction behavior.

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
