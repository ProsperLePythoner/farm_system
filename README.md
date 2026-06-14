# Agribusiness_Architechture

## Project Overview

### Project Name
Agribusiness Management System

### Mission
Build a simple, reliable farm operations system that replaces paper records and helps manage:

- Crop planting
- Harvest tracking
- Customer records
- Orders
- Payments

The system should prioritize:

1. Simplicity
2. Reliability
3. Fast data entry
4. Easy maintenance
5. Future scalability

Version 1 is intentionally small and focused.

---

## Version 1 Goals

### Problem 1: Crop Lifecycle Management

Track:

- Crops
- Planting dates
- Expected harvest dates
- Harvest records

Benefits:

- Never forget planting dates
- Automatically predict harvest windows
- View upcoming harvests
- Receive harvest reminders

---

### Problem 2: Customer & Sales Management

Track:

- Customers
- Orders
- Payments
- Outstanding balances, i.e. [...]

Benefits:

- Eliminate paper records
- Reduce lost information
- Quickly retrieve customer history
- Monitor unpaid balances

---

## Technology Stack

### Backend

- Django

Responsibilities:

- Authentication
- Business logic
- Database interaction
- Notifications

---

### Database

- PostgreSQL

Reasons:

- Free
- Reliable
- Fast
- Excellent Django integration
- Easy migrations

### Frontend

Version 1:

- Django Templates
- HTML
- CSS
- JavaScript

Avoid React until there is a clear business need (and of course until you've actually learned some of it 🥲)

---

## Core Design Philosophy

### Store Facts, Calculate Results

Store:

- Planting dates
- Harvest records
- Orders
- Payments

Calculate:

- Harvest windows (i.e. maturity duration)
- Available stock
- Outstanding balances

Avoid duplicate data whenever possible.

---

## Project Structure

```
farm_system/
│
├── config/
│
├── apps/
│   ├─- accounts/
│   ├── crops/
│   ├── harvests/
│   ├── customers/
│   ├── sales/
│   └── dashboard/
│
├── templates/
│   ├── base/
│   ├── accounts/
│   ├── dashboard/
│   ├── crops/
│   ├── harvests/
│   ├── customers/
│   └── sales/
│
├── static/
│   ├── css/
│   ├── js/
│   ├── images/
│   └── fonts/
│
├── media/
│
├── requirements.txt
|
├── README.md
│
└── manage.py
```

## App Responsibilities

### accounts

Handles:
- Login
- Logout
- Permissions
- User roles

Roles:
- Admin
- Staff

---

### crops

#### Crop [each one]

Fields:
- name
- maturity_days
- unit
- description

Example:

Tomatoes
- maturity_days = 90
- unit = kg

---

#### Planting

Fields:
- crop
- planting_date
- field_name

Status values:
- PLANTED
- READY_FOR_HARVEST
- HARVESTED

---

### harvests

#### Harvest

Fields:
- planting
- harvesting_date
- quantity_harvested
- notes

Relationship:
Crop
⇣
Planting
⇣
Harvest

A planting can have multiple harvest records.

Example:

Planting: Tomatoes

Harvest 1: 150kg
Harvest 2: 120kg
Harvest 3: 90kg

---

### customers

#### Customer

Fields:
- name
- phone
- location
- notes
- created_at

---

### sales

#### Order

Fields:
- customer
- order_date
- total_amount

---

#### Payment

Fields:
- order
- amount_paid
- payment_date

Outstanding balance should always be calculated.

Never use a simple paid/unpaid Boolean, i.e. this is unrealistic

---

### dashboard

Displays:
- Upcoming harvests
- Available stock
- Oustanding balances
- Recent orders

Contains no business logic.

---

## Harvest Window Logic

Harvest Start:
planting_date + maturity_days

Harvest End:
harvest_start + 3 days

These values should be calculated dynamically.

Do not store them initially.

---

## Inventory Strategy

Version 1 does not require a dedicated inventory app.

Available Stock:

### Total Harvested [to_be_reviewed!!]

Total Sold

=

Available Stock

Example:

Harvested = 500kg
Sold = 320kg

Available = 180kg

Create a dedicated inventory app only when inventory complexity justifies it.

---

## Calendar Feature

Required.

Calendar should display:
- Planting dates
- Harvest windows
- Upcoming harvests

Primary view:
Month Calendar (with days, ofc.)

---

## Notification System

Version 1:

Use email reminders to notify farmers on harvests due within 3 days.

Future options to consider:
- SMS
- WhatsApp
- Push notifications

---

## Authentication Strategy

Version 1:
- Django Authentication
- Username
- Password

Do **not** implement:
- Google Login
- Facebook Login
- OAuth Providers

For all the right reasons, do *NOT*. Besides, this is just version 1 🤷‍♀️...

Only do employ this stuff to work when a *real* need exists.

---

## Future Features (Not Version 1)

Potential future additions:

- Weather Integration
- Expense Tracking
- Employee Management
- Yield Analytics
- Mobile App
- Inventory App
- Customer Invoicing
- AI Forecasting

These features should not influence Version 1 architecture.

---

## Development Roadmap

### Sprint 1

- Authentication
- Crop CRUD
- Planting CRUD
- Customer CRUD

### Sprint 2
- Harvest Recording
- Orders
- Payments
- Outstanding Balances

### Sprint 3
- Dashboard
- Calendar
- Email Notifications

### Sprint 4
- Deployment
- User Testing
- Bug Fixes

---

## Golden Rule

Before adding any feature ask:

"Does this solve a real farm problem today?"

If the answer is no: do not build it yet.