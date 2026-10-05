# Database Design

This document records the current model relationships and the important
boundaries between production and sales. Django supplies each model's primary
key automatically unless one is explicitly declared.

## Current entities and relationships

### Field

- Stores a named physical block, plot, or greenhouse, its size in acres, and
  optional notes.
- Has many plantings.
- Fields with plantings are protected from deletion.

### Crop

- Stores the crop name, maturity duration in days, measurement unit, and
  optional description.
- Measurement units are currently selected from a controlled list (`g`, `kg`,
  `tonne`, `bag`, `crate`, `bunch`, `heads`, and `pcs`). Existing `heads` and
  `pcs` records are retained.
- Has many plantings.
- Crops used by plantings or order items are protected from deletion.

### Planting

- Belongs to one crop and one field.
- Stores planting date, planted quantity and its unit, and optional notes.
- Has many harvest records.
- Calculates the expected harvest start from planting date plus crop maturity
  days; the current window spans three calendar days, ending at start plus two
  days.

### Harvest

- Belongs to one planting.
- Stores harvest date, quantity, the unit used for that record, and optional
  notes.
- A harvest date cannot be earlier than its planting date; quantity must be
  positive.
- The unit is stored on the harvest so later edits to the crop catalogue do not
  relabel historical harvests.
- A planting with harvest records cannot be deleted.

### Customer

- Stores a person/business name, phone, optional location, notes, and creation
  timestamp.
- Has many orders.

### Order

- Belongs to one customer and stores order date, notes, and timestamps.
- Has many order items and payments.
- Calculates total amount, total paid, outstanding balance, and payment status
  from related records.

### OrderItem

- Belongs to one order and references one crop.
- New order items also reference one specific harvest; the crop is set from that
  harvest.
- Stores quantity, the unit snapshot, and unit price; line total is calculated.
- `harvest` is nullable only to preserve older crop-only sales that cannot be
  assigned to a harvest without inventing historical allocation data.

### Payment

- Belongs to one order and stores payment amount and date.

## Relationship summary

```text
Crop      1 ─── * Planting * ─── 1 Field
Planting  1 ─── * Harvest
Customer  1 ─── * Order
Order     1 ─── * OrderItem * ─── 1 Crop
Harvest   1 ─── * OrderItem (harvest nullable on legacy items only)
Order     1 ─── * Payment
```

## Inventory and traceability boundary

New sales items are assigned to a specific harvest record, which provides a
basis for harvest-level stock calculations. Older order items still reference
only a crop and are retained as legacy data; they cannot be safely allocated to
a harvest retrospectively.

Stock availability is not yet calculated or enforced. Before doing so, define:

1. When stock is reduced (for example, on order confirmation or fulfillment).
2. How waste, returns, adjustments, and negative stock are represented.
3. How legacy crop-only order items should be handled in stock reports.

Each new order item snapshots the harvest's unit, and its crop is taken from that
harvest. Do not treat `harvested quantity - linked order quantities` as
authoritative stock until movement and fulfillment rules are settled.

## Notes on model deletion behavior

- Deleting an order cascades to its order items.
- Orders with payment history cannot be deleted.
- Deleting a planting that has harvest records is prevented.
- Deleting a harvest referenced by an order item is prevented.
- Referenced crops and fields are protected from deletion through their
  relationships.

## Apps and models

```text
accounts
└── Uses Django's built-in user model (no custom user model currently defined)

crops
├── Crop
├── Field
└── Planting

harvests
└── Harvest

customers
└── Customer

sales
├── Order
├── OrderItem
└── Payment
```

## Database engine

Project settings currently configure PostgreSQL. A local SQLite database file
is also present in the repository directory, but it is not the database engine
configured by the current settings.
