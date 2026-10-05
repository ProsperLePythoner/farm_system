# Development Roadmap

This document describes the current implementation and the next steps for the
Agribusiness Management System. A checked item means the functionality exists in
the application; it does not imply production hardening.

## Current state

### Project foundation

- [x] Django project split into domain apps: accounts, crops, harvests,
  customers, sales, and dashboard.
- [x] Django admin is configured for the primary production and customer models.
- [x] Crop, field, planting, customer, harvest, order, order-item, and payment
  model foundations exist.
- [x] Migrations exist for the current models.

### Production workflow

- [x] Planting list, create, detail, update, and delete pages.
- [x] Planting records include crop, field, planted quantity/unit, and date.
- [x] Expected harvest dates are calculated from crop maturity days.
- [x] Harvest list and record, edit, and delete pages.
- [x] Harvest list shows future planting-based expected windows and links to the
  record form for each planting.
- [x] A harvest is recorded from its planting and captures the harvest quantity,
  date, unit, and notes.
- [x] Harvest dates before a planting date and non-positive harvest quantities
  are rejected.
- [x] Plantings with harvest records cannot be deleted, preserving production
  history.
- [x] Customer list, detail, create, edit, and delete workflows.
- [x] Customer detail displays related order history.
- [x] Customer records with orders are protected from deletion.

### Incomplete foundations

- [ ] Crop and field user-facing pages; the current crop views focus on
  plantings.
- [ ] Order, order-item, and payment workflows.
- [ ] Inventory calculations and stock availability checks.
- [ ] Role-based access control; the planned roles are not yet enforced.
- [ ] Operational dashboard, reporting, notifications, and deployment setup.

## Recommended next steps

1. Finish crops and fields management, or decide that these master records will
   remain admin-only for the first release.
2. Implement order and payment workflows, with validation and tests around
   totals, payment balances, and invalid input.
3. Decide and enforce quantity-unit rules before calculating stock:
   - either make a crop's unit immutable once it has related transactions, or
   - preserve the unit on each sales order item, as harvests already do.
4. Define inventory semantics, including whether negative stock is allowed,
   how returns/waste are represented, and when an order reduces available stock.
5. Build a dashboard from implemented production and sales queries; avoid
   presenting planned metrics as if they are already authoritative.
6. Add authentication, role/group permissions, and access tests before
   multi-user deployment.
7. Configure production settings, credentials, database, static/media files,
   backups, and deployment checks.

## Later enhancements

- Harvest-window email or in-app alerts, with delivery timing and recipient
  rules defined first.
- Reports for production, sales, outstanding balances, and stock.
- Batch-level traceability, if a sale must be tied to a particular harvest.

## Current inventory boundary

Harvest records are production history. They are not stock batches allocated to
sales. The current sales model associates an order item with a crop, not with a
harvest. Crop-level stock can only be calculated reliably after harvest and sales
units are made consistent and business rules for stock movements are defined.
