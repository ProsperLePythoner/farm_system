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
- [x] Sales order list, detail, create, edit, and delete workflows.
- [x] Orders support multiple line items linked to specific harvest records.
- [x] Order totals and outstanding balances are calculated from line items and
  existing payment records.
- [x] Orders with payment history and harvests referenced by sales are protected
  from deletion.

### Incomplete foundations

- [ ] Crop and field user-facing pages; the current crop views focus on
  plantings.
- [ ] Payment creation and management workflows.
- [ ] Inventory calculations and stock availability checks.
- [ ] Role-based access control; the planned roles are not yet enforced.
- [ ] Operational dashboard, reporting, notifications, and deployment setup.

## Recommended next steps

1. Finish crops and fields management, or decide that these master records will
   remain admin-only for the first release.
2. Implement payment creation and management, with validation and tests around
   payment balances and invalid input.
3. Define inventory semantics, including when stock is deducted, whether
   negative stock is allowed, and how waste, returns, and adjustments are
   represented.
4. Enforce harvest-level availability so order quantities cannot exceed
   remaining stock.
5. Revisit legacy crop-only sales: they remain readable but cannot be assigned
   to harvest stock without historical allocation data.
6. Build a dashboard from implemented production and sales queries; avoid
   presenting planned metrics as if they are already authoritative.
7. Add authentication, role/group permissions, and access tests before
   multi-user deployment.
8. Configure production settings, credentials, database, static/media files,
   backups, and deployment checks.

New order items snapshot the selected harvest's measurement unit. Legacy
crop-only order items remain readable, but cannot be assigned to harvest stock
without historical allocation data.

## Later enhancements

- Harvest-window email or in-app alerts, with delivery timing and recipient
  rules defined first.
- Reports for production, sales, outstanding balances, and stock.
- Harvest-level stock reporting and adjustments, once movement rules are defined.

## Current inventory boundary

New sales lines reference harvest records, but stock availability and
overselling validation are not implemented. Do not treat harvested quantity
minus order quantities as authoritative until order fulfillment, returns, and
adjustment rules are defined.
