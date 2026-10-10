# Account Management and Permissions

The application uses Django's built-in `User`, `Group`, and model
permissions. It does not use public registration or a custom user model.
This feature adds no database models or schema migrations. Apply any pending
project migrations before running the role setup command:

```powershell
python manage.py migrate
python manage.py setup_roles
```

`setup_roles` is safe to run repeatedly. It creates the standard groups and
replaces each group's permissions with the documented defaults. It never
creates users, sets passwords, promotes existing users, or changes
`is_staff`/`is_superuser`.

## Roles

| Role | Access |
| --- | --- |
| Administrator | Full operational model permissions and application user administration. Cannot grant superuser or Django admin status; only a trusted superuser can assign the Administrator role or edit another Administrator account. |
| Farm Manager | Full operational model permissions for crops, fields, plantings, harvests, customers, orders, order items, and payments. Existing record-protection rules still apply. |
| Harvest Manager | Read crops, fields, and plantings; create, view, and update harvest records. Cannot delete harvests or access customer/sales/payment or user-management pages. |
| Sales Manager | Read crop, field, planting, and harvest information; create, view, and update customers, orders, order items, and payments. Cannot change production records or delete customers or financial records. |
| Staff | Read-only crop, field, planting, harvest, customer, order, and order-item information. Payment permissions, balances, and payment status are not exposed. |

All roles require authentication to access the dashboard and operational
pages. Sidebar and page actions reflect permissions for convenience; the
server-side checks on each view are authoritative. Django's `/admin/` remains
restricted to users with `is_staff`; membership in the application
Administrator group does not grant it.
Authenticated accounts without one of the recognized application roles can
update their own profile but are denied the dashboard and operational
modules. The development-only `/testing/` utilities also require sign-in.

The current application has no payment-entry pages. The Sales Manager and
Farm Manager permissions include the relevant payment model permissions for
the existing business workflow, but a future payment UI must enforce those
permissions and payment validation rules.

## Creating the first application Administrator

Use a trusted operator account to bootstrap application administration:

1. Apply migrations and run `python manage.py setup_roles`.
2. If no trusted Django superuser exists, run `python manage.py createsuperuser`
   from the trusted deployment/development environment. Do not share or
   commit its password.
3. Sign in at `/accounts/login/` as that superuser.
4. Open **User Accounts**, create the first application user, choose
   **Administrator**, and explicitly enable the account if it should be able
   to sign in immediately.
5. Sign out and sign in as the application Administrator to manage
   non-administrator accounts.

The superuser can continue to administer the application and Django admin.
An Administrator group member is not a superuser and is not automatically
allowed into Django admin. Administrators cannot assign the Administrator
role, modify other Administrators, grant Django admin/superuser status, or
deactivate themselves. The UI also prevents deactivating the last active
trusted administrator.

## Sign-in and profile behavior

- Sign in with the Django username and password at `/accounts/login/`.
- Logout is a CSRF-protected POST action.
- An inactive account cannot sign in; deactivating an account also prevents
  its authenticated session from continuing to access protected pages.
- Administrators create accounts; there is no self-registration. Newly
  created accounts are inactive unless the administrator explicitly enables
  them.
- Users can update only their own first and last name at `/accounts/profile/`.
  Those names appear in the top bar; the username is shown if no name is set.
- Editing a user account does not expose password hashes or permit password
  edits. A dedicated password-reset workflow is not currently included.

Role assignment is a single application role per managed account. Existing
user accounts and data are preserved; the setup command does not assign
roles to existing users.
