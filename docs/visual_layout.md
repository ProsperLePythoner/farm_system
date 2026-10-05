# Visual Layout

## Current shared application shell

The web UI currently uses a shared Django template shell:

```text
+--------------------------------------------------------------+
| Navbar                                                       |
+--------------------+-----------------------------------------+
| Sidebar            | Main content                            |
|                    |                                         |
| Dashboard          | Current app page                        |
| Crops/Plantings    |                                         |
| Harvests           |                                         |
| Customers          |                                         |
| Sales              |                                         |
| Reports            |                                         |
+--------------------+-----------------------------------------+
| Footer                                                       |
+--------------------------------------------------------------+
```

The shell is defined in `templates/base/base.html`. The sidebar includes
navigation entries for several areas, but not every entry currently leads to an
implemented feature.

## Current page coverage

- **Plantings:** list, form, detail, and delete confirmation pages.
- **Harvests:** list, record/edit form, and delete confirmation pages; planting
  detail includes that planting's harvest history.
- **Dashboard:** shared shell only; no operational metrics yet.
- **Customers and sales:** templates and/or views are incomplete and should not
  be represented as finished workflows.

## Intended navigation

```text
Dashboard
├── Production
│   ├── Crops and fields
│   ├── Plantings
│   └── Harvests
├── Sales
│   ├── Customers
│   ├── Orders
│   └── Payments
├── Reports
└── Administration
```

This is a target information architecture, not a guarantee that every menu
destination is implemented. The navigation should mirror business tasks rather
than expose database tables directly.

## Future dashboard content

Once the underlying workflows and rules exist, the dashboard can surface:

- plantings approaching or within their expected harvest window;
- recent harvest records;
- production and sales summaries;
- inventory warnings, after unit and stock movement rules are implemented;
- role-appropriate quick actions, after permissions are in place.
