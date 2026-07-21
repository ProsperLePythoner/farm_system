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
Design the production side first.

## Workflow A — Planning a crop
Suppose today is the beginning of the season. The manager wants to grow tomatoes.
The workflow is:
```text
Dashboard
        │
        ▼
View Crops
        │
        ▼
Choose Tomatoes
        │
        ▼
Create Planting
        │
        ▼
Select Field
        │
        ▼
Enter planting date
        │
        ▼
Save
```
Question:<br>
Why don't we create a crop here?
Because tomatoes already exist in the crop catalogue.
We're planting tomatoes.
That's a different action.
The separation makes data much cleaner.

---

## Workflow B — Harvesting
A month later...

The dashboard says:

```text
Planting #27

Ready for harvest
```
Manager clicks:
```text
Record Harvest
```

The page already knows:
- planting
- crop
- field

The manager only enters:
```text
Harvest Date

Quantity

Notes
```

The form, as well as the url become quite simple, 
e.g. ```/plantings/27/harvests/new/```, 
instead of: ```/harvest/create/```

This is called *context-aware workflow*. The URL carries the context, 
so the form doesn't have to ask for information the system already knows.

---

## Workflow C — Selling produce
Now we switch roles.

The sales clerk logs in.

Their dashboard looks completely different.
```text
Dashboard

Customers

Recent Orders

Outstanding Payments

Quick Sale
```

Suppose a customer walks in. The clerk follows this path:
```text
Dashboard
      │
      ▼
Customers
      │
      ▼
Select Customer
      │
      ▼
New Order
      │
      ▼
Add Items
      │
      ▼
Review Total
      │
      ▼
Save Order
```

Then, ```Record Payment```.

Here, "record payment" is a separate workflow. 
A customer may pay immediately, later, or in installments.

That matches how real businesses operate.

---

# Step 4 — Navigation
Now we can derive the application's navigation directly from those workflows.
```text
Dashboard
│
├── Production
│     ├── Fields
│     ├── Crops
│     ├── Plantings
│     └── Harvests
│
├── Sales
│     ├── Customers
│     ├── Orders
│     └── Payments
│
├── Reports
│
└── Administration
```
The menu mirrors the departments of the business, not the database schema.

---

# Step 5 — What views do we actually need?
Now we're ready to think in Django.

Let's take Plantings as an example.

A user needs to:

See all plantings.
View one planting.
Create a planting.
Edit a planting.
Archive (or delete) a planting.

Those map naturally to Django's generic class-based views:

**Business Task** &emsp; **Django View**

---
| Business task               | Django view                                                         |
| --------------------------- | ------------------------------------------------------------------- |
| List plantings              | `ListView`                                                          |
| View planting details       | `DetailView`                                                        |
| Register a new planting     | `CreateView`                                                        |
| Update planting information | `UpdateView`                                                        |
| Archive/remove planting     | `DeleteView` (or a custom archive view if you prefer soft deletion) |

The key point is that we're choosing these views because they fit 
the business tasks, not because "CRUD is what Django apps have."

--- 
<br>

### `Courtesy of ChatGPT...`
Where we'll start coding

I recommend we begin with the Production module in this order:

Plantings
Harvests
Crops
Customers
Orders
Payments

Why this order?

Because Plantings sit at the heart of your production workflow. 
Harvests depend on plantings, and many dashboard features will 
eventually depend on both. Once those are in place, the rest of the 
application has a solid foundation.

When we start implementing PlantingListView, 
I won't just show you the code. We'll dissect every method and 
attribute—why ListView is the right abstraction, how queryset and 
context are built, why the URL pattern is structured the way it is, 
and how that all supports the business workflow we just designed. 
That understanding will make every subsequent view feel like a logical 
extension rather than a new concept.

---