# Step 1: User Identification
We've got three logical user roles, based on this project.

## 1. Farm Manager
Responsible for production.

They answer questions like:

- What are we growing?
- Where are we planting?
- What's ready for harvest?
- How much have we harvested?

They don't care about customer payments.

---

## 2. Sales Clerk
Responsible for selling produce.

Their world is:

- Customers
- Orders
- Payments
- Outstanding balances

They don't care about planting schedules.

---

## 3. Administrator
Responsible for maintaining the system.

Examples:
- Manage users
- Configure mistakes
- View reports
- Access everything

## `Notice!`
Each role has a **different mental model** 
of the farm.

---

<br>

# Step 2: What happens after login?
If I'm the farm manager, the dashboard should immediately answer the question:
> "What needs my attention today?"

In this context, that might look like:
```text
Dashboard
│
├── Crops currently growing
├── Plantings due for harvest
├── Recent harvests
├── Low inventory alerts
├── Quick actions
│     ├── New Planting
│     ├── Record Harvest
│     └── View Fields
```
Every section answers a real business question.

---

<br>

# Step 3: Build the workflow