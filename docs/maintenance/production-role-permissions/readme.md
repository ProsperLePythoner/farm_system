# Production Role Permissions

## 1. Overview

This directory contains the operational scripts and documentation used to synchronize and verify Django role permissions in the production Agribusiness Management System database.

The enhancement restricts the **Farm Manager** role to agricultural production operations while removing access to sales-related functionality and user account management.

The implementation uses Django's existing centralized role-permission definitions.

### Objectives

- Allow Farm Managers to manage Crops, Fields, Plantings and Harvests.
- Prevent Farm Managers from accessing Customers, Orders, Order Items and Payments.
- Prevent Farm Managers from managing user accounts.
- Ensure production database permissions remain synchronized with the application's source code.
- Provide a repeatable and verifiable procedure for future role-permission updates.

---

## 2. Farm Manager Permission Matrix

| Application area | Model | Permissions |
|---|---|---|
| Crops | Crop | Full CRUD |
| Crops | Field | Full CRUD |
| Crops | Planting | Full CRUD |
| Harvests | Harvest | Full CRUD |
| Customers | Customer | None |
| Sales | Order | None |
| Sales | OrderItem | None |
| Sales | Payment | None |
| Accounts | User | None |

CRUD represents:

- **Create:** Add records.
- **Read:** View records.
- **Update:** Modify records.
- **Delete:** Remove records.

The Farm Manager retains full access to the four agricultural production models but cannot access the restricted sales and account-management models.

---

## 3. Implementation Details

### Centralized permission definitions

**File:** `apps/accounts/roles.py`

The Farm Manager role was changed from the broad `ALL_OPERATIONAL_PERMISSIONS` definition to explicit model-level permissions.

The new definition grants:

- `view`
- `add`
- `change`
- `delete`

For:

- Crop
- Field
- Planting
- Harvest

No permissions are assigned to the restricted sales models.

### Automated permission tests

**File:** `apps/accounts/tests.py`

The existing permission tests were updated to verify:

- Full CRUD permissions for production models.
- No CRUD permissions for sales models.
- No user-management permissions.
- Restricted HTTP access to customer and sales endpoints.
- Continued access to permitted production functionality.

### Dashboard reminder recipients

**File:** `apps/dashboard/reminders.py`

Farm Managers were removed from payment reminder recipients.

Payment reminders now target:

- Administrator
- Sales Manager

This prevents Farm Managers from receiving sales-related payment reminders.

### Dashboard regression tests

**File:** `apps/dashboard/tests.py`

A regression test was added to ensure Farm Managers receive harvest-related reminders but not payment digests.

### Documentation

**File:** `docs/user_roles_and_permissions.md`

The existing role-permission matrix was updated to reflect the new restrictions.

---

## 4. Production Database Synchronization

### Why synchronization was necessary

Changing permission definitions in Python does not automatically update permissions already assigned to Django Groups in the production database.

The production database therefore needed to be synchronized with the updated definitions.

### Management command

The existing Django management command was used:

```powershell
python manage.py setup_roles
```

The command synchronizes group permissions using the centralized role definitions.

It uses `group.permissions.set(...)`, ensuring permissions removed from the definitions are also removed from the corresponding database groups.

No schema migration was required.

### Production database connection

The production database is hosted on Neon PostgreSQL.

The local Django configuration reads the `DATABASE_URL` environment variable.

A temporary environment file was used to supply the production connection string:

`.env.production.local`

This file must remain excluded from Git.

A separate Python process was used to ensure Django received the intended production environment variable without changing the existing local `.env` configuration.

---

## 5. Production Recovery Preparation

Before synchronization:

1. Opened the Neon Console.
2. Identified the production database branch.
3. Checked the project's history retention window.
4. Created a separate recovery branch named:

   `pre-role-permissions`

5. Used the current production data as the branch snapshot.

The Neon project had the expected six-hour history window.

The recovery branch provides an isolated copy of the database from before the permission synchronization.

It should be retained until the production changes have been fully validated.

---

## 6. Production Synchronization Results

The production synchronization command completed successfully.

The following Django groups were updated:

- Administrator
- Farm Manager
- Harvest Manager
- Sales Manager
- Staff

No errors were reported.

---

## 7. Production Verification

Verification was performed against the production Neon database, not the local development database.

### Production model permissions

The following results were confirmed:

| Model | Result |
|---|---|
| Crop | Full CRUD |
| Field | Full CRUD |
| Planting | Full CRUD |
| Harvest | Full CRUD |
| Customer | No permissions |
| Order | No permissions |
| OrderItem | No permissions |
| Payment | No permissions |

All eight model checks produced the expected results.

### User-management permissions

The Farm Manager group's permissions were queried for the Django `accounts.User` model.

Result:

```text
User-management permissions:
PASS: No user-management permissions.
```

The production database therefore reflects the intended Farm Manager permission configuration.

---

## 8. Future Maintenance Procedure

Whenever role definitions are changed:

1. Update the centralized definitions in `apps/accounts/roles.py`.
2. Update the corresponding tests in `apps/accounts/tests.py`.
3. Update relevant dashboard tests if reminder recipients change.
4. Update `docs/user_roles_and_permissions.md`.
5. Run the Django test suite.
6. Deploy the approved changes to production.
7. Create or confirm a suitable Neon recovery point.
8. Connect to the production database using the secure environment-file procedure.
9. Run `setup_roles`.
10. Run the production permission verification script.
11. Test the relevant functionality through the deployed application.

**Important:** Always verify the target database hostname before running database-modifying commands.

Never execute production synchronization against `localhost` unintentionally.

---

## 9. Security Considerations

- Never commit `.env.production.local`.
- Never place database credentials in Python scripts.
- Never share production connection strings in logs, documentation or source control.
- Keep production verification separate from local development verification.
- Retain the recovery branch until the changes have been validated.
- Do not use the recovery branch as the application's normal database connection.

---

## 10. Final Status

**Production role-permission synchronization: Successful**

The Farm Manager role has been restricted to agricultural production operations in the production database.

The centralized permission definitions, tests, dashboard reminder logic and role documentation have been updated to reflect the new access policy.

The production database synchronization and permission verification completed successfully.