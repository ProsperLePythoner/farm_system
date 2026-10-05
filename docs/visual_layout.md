# Visual Layout

## Current shared application shell

The web UI uses a shared Django template shell styled by the project's
hand-written `static/css/base.css`. The sidebar is vertical on wider screens
and becomes one horizontally scrollable navigation row on smaller screens:

```text
+--------------------------------------------------------------+
| Navbar                                                       |
+--------------------+-----------------------------------------+
| Sidebar            | Main content + flash messages           |
|                    |                                         |
| Dashboard          | Current app page                        |
| Crops & Production |                                         |
|   Crops/Fields     |                                         |
|   Plantings        |                                         |
|   Harvests         |                                         |
| Customers          |                                         |
| Sales              |                                         |
+--------------------+-----------------------------------------+
| Footer                                                       |
+--------------------------------------------------------------+
```

The shell is defined in `templates/base/base.html`. Navigation covers the
dashboard landing page, crop/field/planting workflows, harvests, customers, and
sales orders. Active-page links use a consistent accent treatment.

## Current page coverage

- **Plantings:** list, form, detail, and delete confirmation pages.
- **Crops and fields:** overview, list, detail, form, and delete confirmation
  pages.
- **Harvests:** list, record/edit form, and delete confirmation pages; planting
  detail includes that planting's harvest history.
- **Dashboard:** landing page in the shared shell; no operational metrics yet.
- **Customers:** list, detail with order history, create, edit, and delete.
- **Sales:** order list, detail, create/edit with harvest-linked items, and
  delete.

## Navigation structure

```text
Dashboard
├── Production
│   ├── Crops and fields
│   ├── Plantings
│   └── Harvests
├── Customers
└── Sales Orders
```

Payments, reports, and administration are intended destinations but do not yet
have dedicated user-facing workflows. Navigation should mirror business tasks
rather than expose database tables directly.

## Future dashboard content

Once the underlying workflows and rules exist, the dashboard can surface:

- plantings approaching or within their expected harvest window;
- recent harvest records;
- production and sales summaries;
- inventory warnings, after unit and stock movement rules are implemented;
- role-appropriate quick actions, after permissions are in place.
