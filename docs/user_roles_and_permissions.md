# User Roles & Permissions

This document outlines the permissions assigned to each user role within the **Agribusiness Management System**.

The permissions listed below reflect the actual enforcement defined in `roles.py`, rather than a conceptual description of intended functionality.

## 1. Permission Matrix

The following abbreviations are used:

| Code | Permission |
|:---:|---|
| **V** | View |
| **A** | Add |
| **E** | Edit |
| **D** | Delete |
| **—** | No access |

### Operational Permissions

| Area | Administrator | Farm Manager | Harvest Manager | Sales Manager | Staff |
|---|:---:|:---:|:---:|:---:|:---:|
| Crops, Fields & Plantings | VAED | VAED | V--- | V--- | V--- |
| Harvests | VAED | VAED | VAE- | V--- | V--- |
| Customers | VAED | VAED | ---- | VAE- | V--- |
| Orders | VAED | VAED | ---- | VAE- | V--- |
| Payments | VAED | VAED | ---- | VAE- | ---- |

### Account Management

| Capability | Administrator | Farm Manager | Harvest Manager | Sales Manager | Staff |
|---|:---:|:---:|:---:|:---:|:---:|
| Manage User Accounts | Yes | No | No | No | No |

---

## 2. Role Descriptions

### Administrator
- Has full operational access across all system modules.
- Can view, add, edit and delete operational records.
- Can create and edit user accounts.
- Cannot assign the Administrator role to other users.

### Farm Manager
- Has full operational access across all system modules.
- Can view, add, edit and delete operational records.
- Does not have permission to manage user accounts.

### Harvest Manager
- Can view crops, fields and plantings.
- Can record and edit harvest records but cannot delete them.
- Has no access to customers, orders or payment information.

### Sales Manager
- Can manage customers, orders and payments.
- Can view, add and edit these records but cannot delete them.
- Can view crops and harvests for reference when creating orders.
- Cannot modify crop or harvest records.

### Staff
- Has read-only access to operational information.
- Cannot add, edit or delete records.
- Has no access to the Payments module.
- Financial information, including amounts paid and outstanding balances, is hidden.

### Users Without an Assigned Role
- Can successfully authenticate and sign in.
- Have no access to application modules or protected pages.
- All protected page requests return an HTTP **403 Forbidden** response.

---

## 3. Additional Permission Rules & Implementation Details

The following details are particularly important because they describe behaviours that are not immediately obvious from the permission matrix.

### 3.1 Deletion Restrictions
Only the following roles can delete operational records:
- Administrator
- Farm Manager

All other roles are restricted from deleting records, regardless of their access to the relevant module.

### 3.2 Payment Recording
The **Record Payment** functionality is available to:
- Administrator
- Farm Manager
- Sales Manager

Harvest Managers and Staff cannot record payments.

### 3.3 Django Admin Site Access
The application roles do not automatically grant Django's `is_staff` permission.

Consequently:
- None of the application roles can access the Django admin site through their assigned roles alone.
- Only Django superusers can access the admin site.
- Payment corrections and other administrative adjustments must therefore be handled through the Django admin site by an authorized superuser.

---

## 4. Important Notes

- Application permissions are enforced by the backend, not merely by hiding or displaying interface elements.
- A user's role determines which operations they can perform.
- Having permission to view a module does not necessarily grant permission to modify its records.
- Financial information is subject to additional access restrictions.

**Source of truth:** `roles.py` and the corresponding permission enforcement throughout the application.

