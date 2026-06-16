# Entities & Attributes

### Farm
- has many Fields

### Field
- has many Plantings

### Planting
- belongs to Crop
- has many Harvests

### Customer
- Own person; purchases and makes orders

### Order
- Belongs to customer
- Has many OrderItem items

### OrderItem
- Belongs to order
- Has a single crop, payment amount, etc.

### Harvest
- belongs to Planting

### Sale
- may contain many Harvest records

<br><br>

# Entity-Relationship Diagram (Rough)

```Python
### Field
1. id
2. name
3. size
4. notes

### Crop
1. id
2. name
3. unit
4. description

### Planting
1. id
2. crop_id (ForeignKey)
3. field_id (ForeignKey)
4. planting_date
5. quantity_planted
6. notes

### Harvest
1. id
2. planting_id (ForeignKey)
3. quantity_harvested
4. harvesting_date

### Customer
1. id
2. name
3. phone
4. location
5. notes

### Order
1. id
2. customer_id (ForeignKey)
3. order_date
4. notes

### OrderItem
1. id
2. crop_id (ForeignKey)
3. quantity
4. unit_price

### Payment
1. id
2. order_id (ForeignKey)
3. amount_paid
4. payment_date
```

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