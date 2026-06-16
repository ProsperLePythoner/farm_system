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
