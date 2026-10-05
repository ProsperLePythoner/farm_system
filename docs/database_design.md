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
- Has many plantings.
- Crops used by plantings or order items are protected from deletion.

### Planting

- Belongs to one crop and one field.
- Stores planting date, planted quantity and its unit, and optional notes.
- Has many harvest records.
- Calculates the expected harvest start from planting date plus crop maturity
  days; the current expected window ends three days later.

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
- Stores quantity and unit price; line total is calculated.
- Does not currently store a unit snapshot or reference a harvest record.

### Payment

- Belongs to one order and stores payment amount and date.

## Relationship summary

```text
Crop      1 ─── * Planting * ─── 1 Field
Planting  1 ─── * Harvest
Customer  1 ─── * Order
Order     1 ─── * OrderItem * ─── 1 Crop
Order     1 ─── * Payment
```

## Inventory and traceability boundary

The current design records harvest production and crop-level sales separately.
An order item is associated with a crop, not a specific harvest. This supports a
future crop-level stock calculation, not batch allocation or full traceability.

Before calculating or enforcing available stock, define:

1. Compatible measurement units between harvests and order items.
2. Whether a crop's unit may change after it has related transactions, or
   whether order items should snapshot their unit.
3. When stock is reduced (for example, on order confirmation or fulfillment).
4. How waste, returns, adjustments, and negative stock are represented.

Do not treat `harvest total - order quantity` as authoritative until these rules
are settled.

## Notes on model deletion behavior

- Deleting an order cascades to its order items and payments.
- Deleting a planting that has harvest records is prevented.
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
