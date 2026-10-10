# AI Implementation Brief: Accounts, Role-Based Access, and User Personalization

## 1. Mission

Implement secure, maintainable user account management in the existing
Django Agribusiness Management System. Users must sign in with a
username and password, be assigned a role, and only access the parts of
the system their role is allowed to use. Display each authenticated
user's real name at the top of the application.

**Work in the existing repository. Inspect before editing. Preserve
working crop, planting, harvest, customer, sales, and dashboard
functionality. Do not rebuild the project or make unrelated redesigns.**

## 2. Existing project context

The repository currently uses:

-   Django with PostgreSQL.
-   Django templates, HTML, CSS, and small amounts of JavaScript where
    already needed.
-   Apps under `apps/`: `accounts`, `crops`, `customers`, `dashboard`,
    `harvests`, `sales`, and `testing`.
-   Project templates under `templates/`, including
    `templates/base/base.html`, `templates/base/navbar.html`, and
    `templates/base/sidebar.html`.
-   Root URL configuration in `config/urls.py`.
-   Settings in `config/settings.py`.
-   `django.contrib.auth`, sessions, messages, and the auth context
    processor are already enabled.
-   `apps.accounts` is installed and `/accounts/` includes
    `apps.accounts.urls`, but the accounts views and URL patterns are
    currently empty.
-   The navbar currently displays `{{ user.get_username }}` when
    authenticated, not the user's full name.
-   The README describes built-in Django authentication with
    username/password and initially lists **Admin** and **Staff** roles.
    This brief expands that into useful job-specific roles without
    adding an external identity provider.

**Security note:** Never read, print, copy, commit, or include secret
values from `.env`. Do not change secrets or database credentials. If
`.env` has accidentally been committed, report that separately rather
than exposing its contents.

## 3. First task: inspect and report

Before making changes:

1.  Inspect `README.md`, `config/settings.py`, `config/urls.py`,
    `config/view_mixins.py`, the `accounts` app, all relevant app URL
    files and views, the base templates, and existing tests.
2.  Identify the current Django version and whether migrations already
    exist or have been applied.
3.  Identify every create, update, delete, and sensitive detail/list
    view in `crops`, `harvests`, `customers`, and `sales`.
4.  Check how current templates and routes are named. Reuse existing URL
    names and template conventions where possible.
5.  Provide a short implementation plan and flag any migration or
    compatibility risks. Then implement the plan; do not stop at a plan
    unless a destructive or genuinely blocking issue requires
    clarification.

## 4. Account and role design

### 4.1 Use Django's built-in user and permission system

Prefer Django's built-in `User`, `Group`, and `Permission` facilities.
Do **not** introduce a custom user model merely to add roles or display
names. The project already has authentication configured, and changing
`AUTH_USER_MODEL` after existing migrations/data can be disruptive.

Use Django Groups as roles and Django model permissions as the
underlying authorization mechanism. Add a small, documented
helper/permission layer only where it improves readability. Do not
implement role checks solely in templates: server-side views must
enforce access.

Use the standard user fields `first_name` and `last_name` for the
person's name. Validate and trim input sensibly. Keep username unique as
Django already does. Do not store passwords in custom fields or logs.

### 4.2 Roles to create

Create these groups and assign permissions idempotently (safe to run
more than once, without duplicating groups or permissions):

1.  **Administrator**
    -   Full application access and user administration.
    -   Can create, edit, deactivate/reactivate users and assign roles.
    -   Can access Django admin only if also granted `is_staff`; do not
        automatically make every application administrator a Django
        superuser.
    -   Only a trusted superuser should be able to grant superuser
        status or alter the highest-level security settings.
2.  **Farm Manager** (general operations manager)
    -   Access to the dashboard and operational modules.
    -   Can manage crops, fields, plantings, harvest records, customers,
        orders, and payments as required for day-to-day operations.
    -   Cannot manage user accounts or change roles.
3.  **Harvest Manager**
    -   Can view relevant crop, field, and planting information needed
        for harvest planning.
    -   Can create and update harvest records.
    -   Should not delete harvest records by default; reserve deletion
        for an administrator or an explicitly authorized manager.
    -   No access to payment administration or user management. Only
        grant sales/customer read access if a real workflow requires it.
4.  **Sales Manager**
    -   Can view customer records and manage customers, orders, order
        items, and payment recording.
    -   Can view available stock/harvest information needed to fulfil
        orders.
    -   Cannot change crop/planting/harvest records, administer users,
        or alter security settings.
    -   Deleting financial records should be restricted. Prefer safe
        business workflows and existing domain rules over destructive
        deletion.
5.  **Staff** (compatibility with the README's original role)
    -   A least-privilege operational role. Start with dashboard and
        read-only access to the operational information required for the
        job; do not grant broad write/delete permissions by default.
    -   If this project has a specific staff workflow already, map it to
        the narrowest suitable permissions and document the mapping.

Role names can be stored as Django Group names. Centralize the canonical
names so view checks and setup code do not rely on inconsistent
spellings.

### 4.3 Permission matrix

Implement and document a permission matrix. Use this as the initial
default; adapt only where the actual app workflows require it.

  ----------------------------------------------------------------------------------------------
  Area /       Administrator   Farm        Harvest Manager      Sales Manager        Staff
  action                       Manager                                               
  ------------ --------------- ----------- -------------------- -------------------- -----------
  Dashboard    Full            View        View                 View                 View

  Crops,       Full CRUD       Full CRUD   Read                 Read for stock       Read
  fields,                                                       context              
  plantings                                                                          

  Harvest      Full CRUD       Full CRUD   Create/read/update   Read for stock       Read
  records                                                       context              

  Customers    Full CRUD       Full CRUD   No access unless     Create/read/update   Read only
                                           required                                  if required

  Orders /     Full access     Full access No access            Create/read/update   Read only
  order items                                                                        if required

  Payments /   Full access     Full access No access            Record/read payments No access
  balances                                                      and balances         by default

  User         Yes             No          No                   No                   No
  accounts and                                                                       
  role                                                                               
  assignment                                                                         

  Django admin Only if         No by       No                   No                   No
  site         `is_staff`;     default                                               
               superuser                                                             
               reserved for                                                          
               trusted                                                               
               operators                                                             
  ----------------------------------------------------------------------------------------------

"Full CRUD" does not override existing business constraints. Avoid
deleting records that are financially or operationally important when a
safer cancellation/deactivation workflow is appropriate. Never rely on
hidden sidebar links as authorization.

## 5. Login, logout, and access behavior

Implement these routes in `apps/accounts/urls.py` with
`app_name = "accounts"` and stable, namespaced names:

-   `accounts:login`
-   `accounts:logout`
-   `accounts:profile`
-   `accounts:user-list`
-   `accounts:user-create`
-   `accounts:user-update`
-   `accounts:user-toggle-active` (or an equivalent safe
    activate/deactivate route)

Use Django's built-in `LoginView` and `LogoutView` where practical, with
project templates and messages. Logout must be a POST action with CSRF
protection, not a link that logs a user out via GET. Follow the
installed Django version's supported logout behavior.

Requirements:

-   Unauthenticated users who visit protected application pages must be
    redirected to the login page with a safe `next` return URL.
-   After successful login, return to a safe intended destination or the
    dashboard. Do not permit open redirects to arbitrary external URLs.
-   After logout, redirect to the login page and show a useful message
    if consistent with the project's message patterns.
-   Already-authenticated users visiting the login page should be
    redirected to the dashboard.
-   Invalid credentials must produce a generic, helpful error that does
    not reveal whether a username exists.
-   Protect against CSRF. Use Django's standard password hashing and
    password validation.
-   Do not create public self-registration. This is an internal
    farm-management system; administrators should create accounts.
-   Account creation must use Django's proper user-creation form/API so
    passwords are hashed and validated.
-   New accounts should be active only when deliberately created/enabled
    by an authorized administrator.
-   Do not allow a user to deactivate themselves or deactivate the last
    active trusted administrator through the normal account-management
    UI.
-   A deactivated user must not be able to log in or continue using
    protected pages.
-   Only administrators may access user-management views. Enforce this
    server-side with decorators/mixins or equivalent checks.
-   Prevent privilege escalation: a normal administrator UI must not let
    a user grant themselves superuser status, change their own role to
    Administrator, or edit other administrators' highest-level
    privileges unless they are a trusted superuser.
-   Do not expose password hashes, reset tokens, or sensitive account
    internals in templates or logs.

## 6. User administration UI

Build clean, functional Django templates under `templates/accounts/`,
matching the existing base template and CSS conventions:

-   `login.html`
-   `profile.html`
-   `user_list.html`
-   `user_form.html` (create and update)
-   Optional confirmation/feedback template if needed

User list should display appropriate non-sensitive fields, such as full
name, username, role/group, active status, and last login. Add clear
links/actions for creating and editing users and activating/deactivating
them. Do not expose admin-only controls to other roles, and do not rely
on the UI for enforcement.

The user form should include first name, last name, username, role, and
active status where appropriate. For create, include password and
confirmation fields via a secure Django form. For edit, do not display
or edit the stored password directly; provide a separate safe
password-change/reset workflow only if included in scope.

Use Django forms and server-side validation rather than manually
trusting POST values. Add success/error messages. Use POST for all
state-changing operations, including activate/deactivate, with CSRF
tokens.

## 7. Display the signed-in user's name at the top

Update `templates/base/navbar.html` so the top bar displays a friendly
name:

-   Prefer `user.get_full_name` when both/one name fields are populated.
-   If no first/last name has been set, fall back to
    `user.get_username`.
-   Show the user's role in a small secondary label if it can be done
    cleanly (for example, "Sales Manager"); do not display raw internal
    permission names.
-   Link the name to `accounts:profile`.
-   Show a clear logout control for authenticated users; submit logout
    via POST with a CSRF token.
-   For anonymous users, show a login link rather than a blank user
    area.

Do not hardcode a person's name. The value must come from the
authenticated Django user object. Keep the name visible at the very top
on all pages that extend `base/base.html`.

Add/update profile functionality so users can update their own first and
last name (and any safe basic profile fields included). Users must not
be able to edit their username, role, active status, permissions, or
other account privileges through their own profile. If the project
already has a suitable profile view, extend it rather than duplicating
it.

## 8. Enforce permissions throughout the application

This is a security-critical part of the task.

1.  Review all views in `crops`, `harvests`, `customers`, and `sales`,
    including list, detail, create, update, and delete endpoints.
2.  Apply server-side authorization to every protected view. Use Django
    permissions/groups, reusable decorators, or class-based view mixins
    consistently.
3.  Prefer explicit per-view permission requirements or a clearly
    documented reusable policy. Do not create a single overly broad
    "logged in means allowed" rule for every operation.
4.  Check object-level risks where relevant. If a user is not allowed to
    access a module, they must not be able to access its
    detail/edit/delete URL directly.
5.  For unauthorized requests, return a consistent safe result: redirect
    unauthenticated users to login; return 403 or a safe denial page for
    authenticated users lacking permission. Do not silently expose data.
6.  Make the sidebar hide or disable links that the current user cannot
    use, but treat this as a usability feature only; backend checks
    remain authoritative.
7.  Ensure direct access to Django's `/admin/` is governed by Django's
    `is_staff`/superuser checks.
8.  Preserve the dashboard's existing purpose: display summaries, not
    become a place where business logic is duplicated. Do not break
    existing stock, payment, or harvest calculations.

Prefer standard Django model permissions (`view`, `add`, `change`,
`delete`) and Group assignments. If the current views use generic
class-based views, use permission mixins where appropriate. If the app
has custom actions not represented by model permissions, define and test
explicit checks. Avoid scattering unexplained literal group names
through the code.

## 9. Role setup and migrations

Provide a repeatable, safe way to create the role groups and assign
permissions, preferably a Django management command or a data migration
appropriate to the existing migration state.

-   It must be idempotent.
-   Use actual model permissions available after migrations; do not
    assume permissions exist before Django creates them.
-   Explain the exact command to run.
-   Do not create default credentials or hardcoded passwords.
-   Do not silently promote existing users.
-   Do not change `AUTH_USER_MODEL` unless inspection uncovers a
    compelling, documented reason and the migration/data implications
    have been addressed.
-   If permissions depend on custom permissions, create them properly
    and ensure migrations are included.
-   Confirm that existing records and existing user accounts remain
    intact.

## 10. Settings and URL configuration

-   Keep the current settings architecture and environment-variable
    approach.
-   Configure `LOGIN_URL`, `LOGIN_REDIRECT_URL`, and
    `LOGOUT_REDIRECT_URL` using namespaced route names or correct paths.
-   Verify `AuthenticationMiddleware`, session middleware, messages
    middleware, and the auth/messages context processors remain enabled.
-   Add `request` context processor only if needed for template
    authorization/current-route logic; do not remove existing context
    processors.
-   Keep app URL namespaces consistent.
-   Do not change database configuration or production environment
    variables for this task.
-   Check `ALLOWED_HOSTS`, `DEBUG`, and secret settings only for
    regressions; do not put secret values in source code.

## 11. Tests required

Add meaningful automated tests using Django's test framework. At minimum
test:

### Authentication

-   Anonymous users are redirected to login from protected pages.
-   Valid login succeeds and reaches the intended safe
    destination/dashboard.
-   Invalid login fails without disclosing account existence.
-   Logout works only through the intended POST flow and ends the
    session.
-   Inactive users cannot log in.

### Role permissions

-   Each role is assigned the expected groups/permissions.
-   A Sales Manager can access allowed sales/customer workflows but
    cannot mutate crops or harvest records.
-   A Harvest Manager can manage harvest records but cannot access sales
    payment management or user administration.
-   A Farm Manager can access intended operational workflows but cannot
    manage user accounts.
-   Staff has only its explicitly granted permissions.
-   An Administrator can manage accounts, subject to the superuser
    boundary described above.
-   Direct URL requests are denied even when a sidebar link is hidden.
-   Unauthorized POST requests cannot create/update/delete records.

### User management and personalization

-   Only authorized administrators can access user management.
-   User creation hashes passwords and validates them.
-   Role assignment is constrained to allowed roles.
-   A user cannot escalate their own privileges through profile editing.
-   A user's full name appears in the navbar when set.
-   Username is displayed as fallback when no full name is set.
-   Navbar/profile/login/logout behavior works for both authenticated
    and anonymous users.

Use the project's existing test style and factories/fixtures if present.
Tests must not depend on production data or external services.

## 12. Visual and accessibility requirements

-   Reuse `base/base.html`, the existing message system, and current CSS
    conventions.
-   Keep pages usable on desktop and narrow screens.
-   Use labels tied to form fields, keyboard-accessible controls, clear
    focus states, readable error messages, and semantic headings.
-   Avoid introducing a new frontend framework or large dependency.
    Tailwind CSS is planned for a later styling phase; do not migrate
    the app to Tailwind as part of this task.
-   Avoid unnecessary JavaScript. Basic forms and Django templates are
    sufficient.

## 13. Documentation

Update `README.md` or add a concise account/permissions document
explaining:

-   The available roles and their permissions.
-   How an authorized operator creates the first administrator safely.
-   How to run the role setup command.
-   How to create users and assign roles.
-   How login/logout, deactivation, and the displayed full name work.
-   Any intentional limitations or permission decisions.

Do not document or include real passwords, secret keys, or production
credentials.

## 14. Definition of done

The task is complete only when:

-   [ ] Login and logout work end-to-end.
-   [ ] Public self-registration is not exposed.
-   [ ] Role groups and permissions are created repeatably.
-   [ ] All protected application views enforce server-side permissions.
-   [ ] Sidebar links reflect permissions without being treated as the
    security boundary.
-   [ ] Admin-only account management works.
-   [ ] Users can update their own name without changing their role or
    privileges.
-   [ ] The navbar shows full name, falling back to username, at the top
    of every base-template page.
-   [ ] Inactive users are blocked.
-   [ ] Tests cover authentication, role boundaries, direct URL access,
    and personalization.
-   [ ] Existing crop, planting, harvest, customer, sales, payment, and
    dashboard behavior remains intact.
-   [ ] Migrations are included if needed and the role setup is
    idempotent.
-   [ ] README/documentation is updated.
-   [ ] The agent reports changed files, commands run, test results,
    migration commands, and any remaining issues.

## 15. Execution discipline

-   Work incrementally and keep changes scoped to accounts,
    authorization, navigation, and tests.
-   Follow the repository's current architecture and conventions.
-   Do not overwrite unrelated user work.
-   Do not remove existing apps/routes/templates to simplify the task.
-   Do not claim tests pass unless they were actually run; report
    blockers precisely.
-   Before finishing, inspect the diff for accidental `.env`, database,
    secret, or unrelated changes.
-   Give the human operator the exact commands needed to run migrations,
    create/assign roles, and verify the feature locally.
