# Agent Task Brief: Implement User-Friendly HTTP Error Handling

## Project

-   **Repository:** `ProsperLePythoner/farm_system`
-   **Framework:** Django
-   **Project URL configuration:** `config/urls.py`
-   **Project settings:** `config/settings.py`
-   **Shared templates directory:** `templates/`
-   **Shared application shell:** `templates/base/base.html`
-   **Shared view mixins:** `config/view_mixins.py`

## Objective

Implement a small, reliable, user-friendly error-handling system for the
Agribusiness Management System. Users should receive clear guidance when
a request fails, while developers retain enough server-side diagnostic
information to investigate unexpected failures.

Keep the implementation proportionate to the current project. Do not
create a separate Django app solely for error pages, replace existing
URL routing, or refactor unrelated business logic.

## Repository context to verify before editing

The current repository structure includes a shared `templates/`
directory with app template folders for `accounts`, `base`, `crops`,
`customers`, `dashboard`, `harvests`, `sales`, and `testing`.

`config/settings.py` already configures the shared template directory
with `DIRS: [BASE_DIR / "templates"]`, uses `APP_DIRS=True`, and sets
`DEBUG` from the `DJANGO_DEBUG` environment variable, defaulting to
false. It includes `django.middleware.csrf.CsrfViewMiddleware` and
Django messages support.

`config/urls.py` contains the root URL configuration, redirects the site
root to the dashboard, and includes the project's app URL
configurations.

`templates/base/base.html` includes the shared navbar, sidebar, footer,
global stylesheet, and Django messages. Error pages should not depend on
this full shell if doing so could make them fail when another shared
component is involved.

These observations were made from the repository's `main` branch.
**Before editing, inspect the current working tree and relevant files.
The local checkout may contain changes newer than the public branch.
Preserve existing user work and do not overwrite unrelated changes.**

## Tasks

### 1. Inspect the current implementation

-   [ ] Inspect `config/settings.py`, `config/urls.py`,
    `templates/base/base.html`, and `config/view_mixins.py`.
-   [ ] Search the codebase for existing error templates, custom error
    handlers, `handler400`, `handler403`, `handler404`, `handler500`,
    `CSRF_FAILURE_VIEW`, and custom exception middleware.
-   [ ] Review representative CRUD views and forms, particularly the
    crop, field, planting, and harvest workflows.
-   [ ] Identify any existing error-handling patterns or tests and
    extend them rather than duplicating them.
-   [ ] Report any discrepancy between the repository's current state
    and the assumptions in this brief before making structural changes.

### 2. Create the standard error templates

Create the following files in the **root of the shared `templates/`
directory**:

-   [ ] `templates/400.html` --- Bad Request
-   [ ] `templates/403.html` --- Forbidden
-   [ ] `templates/404.html` --- Page Not Found
-   [ ] `templates/500.html` --- Internal Server Error

Requirements for all four pages:

-   [ ] Use valid, accessible HTML with a responsive viewport and a
    meaningful document title.
-   [ ] Match the Agribusiness Management System's general visual style
    without making the pages depend on `templates/base/base.html`.
-   [ ] Provide a concise explanation in plain language and an obvious
    recovery action.
-   [ ] Include a safe link to the site root (`/`), which currently
    redirects to the dashboard.
-   [ ] Avoid broken links to app-specific routes that may themselves be
    unavailable.
-   [ ] Keep the page useful on narrow screens and when JavaScript is
    unavailable.
-   [ ] Do not expose tracebacks, exception messages, SQL, internal
    paths, environment variables, secrets, or customer/business data.
-   [ ] Use a small dedicated stylesheet if styling is needed. Avoid
    duplicating large amounts of global CSS or introducing a frontend
    framework solely for error pages.
-   [ ] Ensure the 500 template is especially minimal and unlikely to
    fail due to dependencies on other templates or context variables.

Suggested user-facing intent:

  -----------------------------------------------------------------------
  Template                            Message intent
  ----------------------------------- -----------------------------------
  `400.html`                          The request could not be processed.
                                      Check the request and try again.

  `403.html`                          You do not have permission to
                                      access this page or perform this
                                      action.

  `404.html`                          The requested page or record could
                                      not be found.

  `500.html`                          An unexpected error occurred. Try
                                      again later or return to the
                                      dashboard.
  -----------------------------------------------------------------------

Do not include a request's raw URL or sensitive request data in the
message.

### 3. Connect the templates to Django

-   [ ] Confirm Django's default error handlers can discover the four
    root-level templates through the existing template configuration.
-   [ ] Prefer Django's built-in error handling unless a concrete
    requirement justifies custom handler functions.
-   [ ] Do not add `handler400`, `handler403`, `handler404`, or
    `handler500` declarations that point to functions that do not exist.
-   [ ] If custom handlers are genuinely needed, implement them in an
    appropriate existing project module or a small `config` module,
    return the correct HTTP status codes, and add tests.
-   [ ] Do not create ordinary URL patterns for the four error pages.
    They are error responses, not normal pages users should navigate to
    directly.
-   [ ] Keep the current root redirect and all app URL includes intact.

### 4. Handle CSRF failures deliberately

-   [ ] Confirm the current CSRF middleware and settings remain enabled.
-   [ ] Decide whether a custom `CSRF_FAILURE_VIEW` is needed for a
    friendlier user experience.
-   [ ] If implementing one, keep it small, use a safe response, and
    optionally add a standalone template such as
    `templates/403_csrf.html`.
-   [ ] Do not disable CSRF checks, exempt ordinary state-changing
    views, or reveal technical CSRF diagnostics to users.
-   [ ] Verify the failure view is correctly configured and tested if
    added.

A dedicated CSRF failure page is optional for this task. Do not
implement one merely to duplicate the ordinary 403 page without adding
useful guidance.

### 5. Preserve correct behavior for form and business-rule errors

Error pages must not replace normal validation and workflow feedback.

-   [ ] Invalid form submissions should normally re-render the original
    form with field-level and non-field errors, preserving valid
    submitted values where appropriate.
-   [ ] Missing model records should normally produce a 404, using
    established Django patterns such as `get_object_or_404()` or generic
    detail views.
-   [ ] Permission failures should respect the existing authentication
    and permission mixins.
-   [ ] Existing protected-delete behavior should continue to explain
    why a record cannot be deleted and must not delete related business
    records.
-   [ ] Business-rule failures, duplicate values, invalid dates, and
    invalid quantities should use form validation or appropriate
    workflow messages where possible.
-   [ ] Do not catch broad exceptions and silently convert every failure
    into a 404 or success message.
-   [ ] Do not change business logic or authorization policy just to
    make an error page appear.

### 6. Review HTTP-method handling

-   [ ] Check whether existing views correctly reject unsupported
    methods.
-   [ ] Add tests for 405 Method Not Allowed behavior where relevant.
-   [ ] Do not add a custom 405 page unless the project has a concrete
    need; a correct status and clear response are sufficient for the
    initial scope.

### 7. Add focused automated tests

Use the project's existing testing conventions. Prefer Django's test
client and test framework unless the repository already uses a different
established approach.

Tests should cover:

-   [ ] With `DEBUG=False`, an unknown URL returns status 404 and
    renders the expected error template.
-   [ ] A nonexistent crop, field, planting, or harvest detail resource
    returns 404 where those routes exist and can be tested with
    appropriate permissions.
-   [ ] A user lacking the required permission receives the intended 403
    behavior.
-   [ ] An anonymous user visiting a login-protected page follows the
    existing redirect-to-login behavior.
-   [ ] Invalid forms remain on the original form and display validation
    errors.
-   [ ] A CSRF-invalid POST is rejected while CSRF protection remains
    enabled.
-   [ ] A controlled unexpected exception produces the intended generic
    500 response in a test setup configured to capture server errors
    rather than re-raise them.
-   [ ] The error pages do not expose exception details or secrets.
-   [ ] Recovery links point to valid, safe destinations.
-   [ ] Existing URL routing, authentication, permissions, and
    protected-delete behavior remain intact.

Testing notes:

-   Django commonly displays technical debugging pages instead of custom
    error templates when `DEBUG=True`. Configure the relevant tests with
    `DEBUG=False`.
-   Django's test client may re-raise unhandled exceptions by default.
    Configure the test client appropriately when asserting a 500
    response; do not weaken production exception handling to accommodate
    the test.
-   Tests involving permissions should create suitable users and
    permissions rather than bypassing the application's access controls.
-   Avoid tests that rely on production data or external services.

### 8. Verify configuration and quality

-   [ ] Run the relevant test suite.
-   [ ] Run `python manage.py check`.
-   [ ] Run any relevant existing linting or formatting commands if
    configured.
-   [ ] Verify the templates are discovered by Django and that the error
    responses carry the expected status codes.
-   [ ] Review the final diff for accidental changes, secrets, debug
    output, unrelated refactors, or generated files.
-   [ ] Do not change production `DEBUG` settings to make local testing
    easier.
-   [ ] Do not add dependencies unless necessary and justified.

## Scope boundaries

Do **not**:

-   Create a new Django app just for error pages.
-   Replace the project's URL structure or dashboard redirect.
-   Disable CSRF, authentication, or permission checks.
-   Expose technical exceptions to users.
-   Turn ordinary form-validation failures into generic error pages.
-   Add elaborate logging infrastructure, custom middleware, or a
    generalized exception framework without a demonstrated need.
-   Modify unrelated models, migrations, business logic, or styling.
-   Commit, push, or deploy changes unless explicitly instructed.

## Acceptance criteria

The task is complete when:

1.  The four standard error templates exist at the shared template root
    and are readable, responsive, and standalone.
2.  Django renders the appropriate template for the relevant HTTP error
    when `DEBUG=False`.
3.  The responses use the correct HTTP status codes.
4.  Form validation, permission checks, CSRF protection, and
    protected-delete business rules continue to work as before.
5.  Focused tests cover the main error paths and pass.
6.  `python manage.py check` passes, and no unrelated changes are
    included.
7.  The agent provides a concise report of files changed, behavior
    implemented, commands/tests run, results, and any remaining
    limitations.

## Final report format

When finished, report:

-   **Files created/modified**
-   **Error scenarios handled**
-   **Tests and checks executed**, with pass/fail results
-   **Any assumptions or limitations**
-   **Any recommended follow-up work**

If a test cannot be run because of missing local services or environment
configuration, state that clearly rather than claiming it passed.
