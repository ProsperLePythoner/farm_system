# Entities & Attributes

### Farm
- has many Fields

### Field
- has many Plantings

### Planting
- belongs to Crop
- has many Harvests

### Harvest
- belongs to Planting

### Sale
- may contain many Harvest records

<br><br>

# Entity-Relationship Diagram (Rough)

### Crop
1. id
2. name
3. variety

## Planting
1. id
2. crop_id
3. field_id
4. planting_date

## Harvest
1. id
2. planting_id
3. quantity
4. harvest_date

<br><br>


# Complete ERD Breakdown (TL;DR ERD 😐)

## 1. Crop → Planting

One crop, e.g. ```tomatoes``` can have multiple plantings:
- March planting
- April planting
- July planting, etc.

In ur models, use:
```Python
Planting.crop = ForeignKey(Crop)
```
<br>

## 2. Field → Planting

One field, e.g. ```Block A``` can have multiple plantings over time:
- Tomatoes
- "Hoho"
- Sweetcorn, etc.

Use:
```Python
Planting.field = ForeignKey(Field)
```
<br>

## 3. Planting → Harvest

From one planting can be harvested ```100pcs, 2000pcs, 1500pcs, etc.``` across multiple harvests.

The appropriate approach to designing this relationship would be:
```Python
Harvest.planting = ForeignKey(Planting)
```
<br>

## 4. Customer → Order

One customer, e.g. ```Msese``` can place multiple orders (```Order 1, ... 2, ... 3```).

For this relationship, use:
```Python
Order.customer = ForeignKey(Customer)
```
<br>

## 5. Order → OrderItem

One order i.e. ```Order #3``` contains multiple order items:
- 200pcs sweetcorn
- 10kg capsicum, etc.

So...
```Python
OrderItem.order = ForeignKey(Order)
```
<br>

## 6. Order → Payment

An order is often paid in instalments. One order that cost ```100,000 TZS``` may be paid through:
- 60,000 TZS
- 30,000 TZS
- 10,000 TZS

Represent it as follows:
```Python
Payment.order = ForeignKey(Order)
```

<br><br>

# Models

```
accounts
└── User

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