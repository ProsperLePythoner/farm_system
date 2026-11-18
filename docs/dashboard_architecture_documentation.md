# Documentation on Dashboard Improvements

## 1. Purpose

The dashboard gives each staff member a role-appropriate overview of the
farm's current operational priorities. It brings harvest activity and
sales information together so users can identify work that needs
attention without opening several separate pages.

The dashboard is designed around three priorities:

-   **Relevant information:** users only receive the sections their role
    is permitted to view.
-   **Actionable summaries:** important records link directly to the
    relevant detail or recording form.
-   **Low-overhead updates:** the page checks for changes periodically
    without requiring a full-page reload.

## 2. What users see

The dashboard is assembled from sections according to the user's
permissions.

### 2.1 Attention summary

A banner at the top reports the number of items requiring action. It
combines:

-   harvest windows that are currently open;
-   harvest windows that have ended without a harvest being recorded;
    and
-   unpaid orders, but only for users permitted to view payment
    information.

If there is nothing requiring attention, the banner displays an
all-caught-up message.

### 2.2 Sales summary

Users with the required sales permissions see the current month's sales
total.

Users who also have permission to view payments see two additional
figures:

-   **Collected this month:** payments recorded during the current
    month.
-   **Still owed:** the combined outstanding balance across unpaid or
    partly paid orders.

The dashboard also shows the number of orders with an outstanding
balance. The unpaid-order list is deliberately limited to the first
eight records so the dashboard remains a summary rather than becoming a
replacement for the full order list.

### 2.3 Harvest activity

Users with the required harvest permissions see planting records grouped
into three operational categories:

-   **Window open now:** plantings whose harvest window includes today.
-   **Window ended, nothing recorded:** plantings whose harvest window
    has passed without a harvest record.
-   **Coming up:** plantings expected to enter their harvest window
    soon.

Where the user has permission to add harvest records, the relevant rows
include a **Record harvest** action. The planting name links to its
detail page.

The harvest section uses the same underlying harvest-window calculation
as the daily email briefing. This keeps the dashboard and email
consistent about which windows are open, missed or approaching.

### 2.4 Fourteen-day harvest agenda

A compact fourteen-day strip shows how many plantings have a harvest
window covering each day. The current day is highlighted, and crop names
are available as a hover hint where applicable.

This is a planning aid: the count represents plantings whose harvest
window includes that date, not a prediction of the quantity that will be
harvested.

### 2.5 Payments to collect

Users with permission to view payments see a short list of unpaid or
partly paid orders. Each entry can show:

-   the order number and customer;
-   the outstanding amount;
-   how many days have passed since the order date;
-   the customer's phone number, as a tap-to-call link when one is
    available; and
-   a **Record payment** action, when the user has permission to add
    payments.

If more than eight orders are unpaid, the dashboard provides a link to
the full order list filtered to unpaid or partly paid orders.

### 2.6 Navigation links

The existing navigation shortcuts remain available in a separate **Go
to** section. Each link is shown only when the user has the
corresponding viewing permission.

## 3. Architecture overview

The dashboard separates responsibility into four layers:

1.  **Configuration** determines the refresh interval.
2.  **Services** calculate and assemble the dashboard data.
3.  **Views and URLs** deliver either the complete page or its
    refreshable content.
4.  **Templates and browser JavaScript** present the information and
    update it without reloading the whole page.

This separation is important for maintenance. Business calculations
belong in the service layer, request handling belongs in the views, and
presentation belongs in templates and static assets. A change to one
responsibility should not require rewriting the others.

## 4. Data assembly and permission boundaries

### 4.1 One dashboard-building entry point

The dashboard service exposes one main operation: build the dashboard
context for a particular user.

It starts with a small, predictable context containing the current local
date and empty placeholders for the harvest and sales sections. It then
checks which sections the user is allowed to access and builds only
those sections.

This means permissions affect more than what appears on screen: they
also determine which data queries are run.

For example, a Harvest Manager who cannot view sales does not trigger
the dashboard's sales queries. This avoids unnecessary database work and
reduces the chance of exposing information through a section that should
not be available to that role.

### 4.2 Section-level permissions

The harvest section requires the relevant viewing permissions for
plantings, crops, fields and harvest records. The sales section requires
the relevant viewing permissions for orders, order items and customers.

Payment information has an additional permission boundary. A user may be
allowed to see sales totals without being allowed to see collected
amounts, outstanding balances or the unpaid-order list.

The dashboard therefore distinguishes between:

-   permission to see the sales section; and
-   permission to see payment information within that section.

### 4.3 Viewing permission is not recording permission

Displaying a section does not automatically grant permission to perform
actions within it.

The service decides whether the user may receive a section's data. The
template separately checks whether the user may see each action link,
such as **Record harvest** or **Record payment**.

This distinction matters because some roles may need to monitor activity
without being allowed to create records. The destination views must
continue to enforce their own permissions as well; hiding a link is a
presentation decision, not a security boundary.

### 4.4 Reusing existing business logic

The dashboard reuses existing application logic rather than introducing
a second definition of the same business rules:

-   Harvest status is obtained through the shared harvest-section
    calculation also used by the email briefing.
-   Outstanding order balances are obtained through the existing
    outstanding-balance queryset logic.
-   Sales totals and payment totals are calculated by database
    aggregation.

Reusing these established calculations reduces duplication and makes
future corrections safer. If the definition of a harvest window changes,
the shared calculation can be updated in one place instead of allowing
the dashboard and email briefing to drift apart.

## 5. How the financial figures are calculated

The financial summary uses the first day of the current month and the
current local date as its date range.

-   **Month-to-date sales** are calculated from order-item line totals,
    using quantity multiplied by unit price, for orders dated within the
    range.
-   **Collected this month** is calculated from payments whose payment
    date falls within the same range.
-   **Outstanding total** is calculated from the outstanding balances of
    orders that still have money due.
-   **Unpaid count** is the number of orders with an outstanding
    balance.

The totals are calculated in the database rather than by loading every
record and adding values in application code. This is more efficient as
the number of orders and payments grows.

The unpaid list is a separate, limited query for the records that need
to be displayed. Each listed order is loaded together with its customer,
avoiding a separate customer lookup for every row.

## 6. Live refresh design

### 6.1 Why polling is used

The dashboard refreshes its data approximately once every 60 seconds
while its browser tab is visible. This is called **polling**: the
browser periodically asks the server whether the dashboard has changed.

Polling is used instead of a persistent WebSocket connection because the
application is hosted on serverless functions. In this hosting model, a
function handles a request and finishes; it is not intended to hold a
continuous connection open for every dashboard user.

The refresh interval is configurable through the
`DASHBOARD_REFRESH_SECONDS` environment setting. Its default is 60
seconds. Increasing it to 120 seconds, for example, reduces the
frequency of refresh requests without requiring a code change.

### 6.2 Full page and partial response

There are two ways to obtain dashboard content:

-   **Full dashboard request:** returns the page, its heading,
    navigation and initial dashboard panels.
-   **Panels request:** returns only the HTML fragment containing the
    changing dashboard panels.

Both paths use the same dashboard-building service and the same panels
template. This is a key consistency rule: the initial page and a later
refresh should present the same information in the same structure.

The panels template is a fragment rather than a complete HTML page. Its
leading underscore is a naming convention that signals this role to
developers.

### 6.3 ETags and unchanged responses

Each panels response is assigned an **ETag**: a fingerprint calculated
from the rendered HTML.

The browser stores the ETag from its last successful response and sends
it with the next request. If the rendered content is unchanged, the
server responds with **304 Not Modified** and no HTML body.

This saves bandwidth because the browser does not need to download and
replace identical content. If the content has changed, the server
responds with the new HTML and a new ETag.

The response also uses `Cache-Control: private, no-cache`. The `private`
directive prevents shared caches from storing one user's dashboard
figures for another user. `no-cache` requires the browser to revalidate
the content before reusing it.

## 7. Browser refresh behaviour and failure handling

The browser-side refresh script is responsible for scheduling requests
and updating the panels. It does not calculate farm or financial
figures; those remain server-side responsibilities.

Its main behaviours are:

-   **No full-page reload:** when new content is returned, only the
    dashboard panels are replaced.
-   **Hidden-tab pause:** scheduled polling stops while the browser tab
    is hidden. When the user returns, the script refreshes immediately
    if the displayed data is at least one refresh interval old.
-   **Manual refresh:** the Refresh button requests an update
    immediately.
-   **Reconnect handling:** when the browser reports that it is online
    again, the script attempts a refresh.
-   **Overlapping-request protection:** a second refresh is not started
    while another request is still in progress.
-   **Failure backoff:** after a failed request, the delay increases
    progressively---60 seconds, 120 seconds, 240 seconds and so on---up
    to ten minutes. This avoids repeatedly hitting a server that is
    unavailable.
-   **Last-known content:** if a refresh fails, the last successfully
    rendered dashboard remains visible and the status text reports that
    the page is offline and retrying.
-   **Session-expiry handling:** the request does not automatically
    follow login redirects. If the session has expired or access is
    denied, polling stops and the user is told to reload the page to
    sign in again.

The status indicator also reports how recently the dashboard was
successfully updated. It is a freshness indicator, not a guarantee that
the server is currently reachable.

## 8. Unpaid-order filtering

The dashboard's **View all unpaid orders** link opens the normal
sales-order list with an unpaid filter.

The filter is only accepted from users who have permission to view
payment information. This check is performed on the server, not merely
by hiding the filter link in the template.

That distinction is important: a user should not be able to discover
payment status by manually adding a query parameter to the URL.

The order list preserves the active filter when the user moves between
pages. If the filter is active but no unpaid orders exist, the page
displays a clear empty-state message.

## 9. Presentation and accessibility

The dashboard uses shared row patterns for harvest tasks and payment
tasks. This keeps the interface visually consistent and makes the
actions easier to find.

The task rows have distinct visual states:

-   **Open:** a harvest window is active.
-   **Missed:** the harvest window ended without a recorded harvest.
-   **Coming up:** the relevant activity is approaching.

The fourteen-day agenda highlights today and days that contain
harvestable plantings. The layout uses a responsive grid for the
financial cards and flexible task rows so that action links remain
usable on narrow screens.

The status and summary areas use semantic status roles, and sections
have accessible labels. These details help assistive technologies
communicate what each part of the dashboard represents.

## 10. Performance considerations

The dashboard is intended for a small farm team and is designed to keep
its queries reasonably bounded.

Current design choices include:

-   permission checks before building optional sections;
-   database-side aggregation for financial totals;
-   related-object loading for displayed unpaid orders;
-   a maximum of eight unpaid orders in the dashboard list;
-   a 304 response when the rendered panels have not changed;
-   no polling while the tab is hidden; and
-   increasing retry delays when the server is unavailable.

The current estimate is approximately ten relatively small queries per
dashboard load or refresh. Each visible dashboard tab polls about once
per minute under normal conditions.

This is considered acceptable for the current scale. If usage or
database load grows, review query counts and response times before
changing the design. Increasing the refresh interval is the simplest
first adjustment.

## 11. Maintenance guide

Use the following ownership boundaries when making future changes.

  -----------------------------------------------------------------------
  If you need to          Start with...           Keep in mind...
  change...                                       
  ----------------------- ----------------------- -----------------------
  Which roles can see     Dashboard service       Keep the permissions
  harvest or sales data   permission checks       aligned with the
                                                  permissions required by
                                                  the corresponding
                                                  application pages.

  Which records count as  Shared harvest          The email briefing and
  open, missed or         calculation             dashboard should
  upcoming harvests                               continue to use the
                                                  same rules.

  Sales, collected or     Dashboard service and   Prefer database
  outstanding totals      existing sales balance  aggregation and reuse
                          logic                   the established balance
                                                  calculation.

  Which dashboard panels  Panels template         The same fragment is
  appear or how they are                          used for the initial
  arranged                                        page and background
                                                  refresh.

  The page heading, date  Main dashboard template Keep navigation links
  or navigation shortcuts                         permission-aware.

  Refresh timing          Environment             The default is 60
                          configuration           seconds; it can be
                                                  increased without
                                                  changing application
                                                  logic.

  Polling, retry          Dashboard JavaScript    Keep hidden-tab
  behaviour or status                             pausing, request
  messages                                        de-duplication and
                                                  failure backoff.

  Response caching or     Panels view             Preserve private
  unchanged-response                              caching and ETag
  behaviour                                       validation.

  Unpaid-order filter     Sales order-list view   Enforce payment
  behaviour               and its template        permission on the
                                                  server and preserve the
                                                  filter through
                                                  pagination.

  Dashboard appearance    Shared stylesheet       Check both desktop and
                                                  narrow-screen layouts.
  -----------------------------------------------------------------------

### Rules worth preserving

1.  **Do not move business calculations into browser JavaScript.** The
    server remains the source of truth for permissions, harvest status
    and financial figures.
2.  **Do not rely on hidden buttons for security.** Views must continue
    to enforce permissions when a URL is opened directly.
3.  **Do not duplicate harvest-window rules.** Keep the dashboard and
    email briefing aligned through the shared service.
4.  **Keep the initial and refreshed panels on the same template.** This
    prevents the dashboard from changing appearance or meaning after a
    refresh.
5.  **Do not remove the private cache policy.** Dashboard figures are
    user-specific.
6.  **Keep refresh requests lightweight.** Return only the panel
    fragment, and retain ETag support so unchanged content does not need
    to be transferred.
7.  **Keep failure behaviour conservative.** A temporary network failure
    should not erase the last good dashboard or trigger rapid repeated
    requests.

## 12. Verification checklist

### Automated checks

-   [ ] Run the full Django test suite.
-   [ ] Confirm the dashboard, cron and email tests pass.
-   [ ] Confirm role-specific dashboard tests cover users with different
    viewing and recording permissions.

The recorded test run for this work passed **135 tests**, including **26
tests** covering the dashboard, cron and email functionality.

### Manual functional checks

-   [ ] Create a planting whose harvest window includes today.
-   [ ] Create an older order with no payment.
-   [ ] Sign in as a Farm Manager and confirm the attention count,
    financial cards, open harvest row and payment row appear as
    expected.
-   [ ] Use **Record harvest** and **Record payment**, save the records,
    and confirm the dashboard reflects the changes.
-   [ ] Sign in as a Harvest Manager and confirm harvest information
    appears without financial or payment information.
-   [ ] Sign in as Staff and confirm sales totals can appear without
    outstanding-balance details.
-   [ ] Confirm users without recording permissions do not see the
    corresponding action links.
-   [ ] Open the browser Network panel and filter requests for `panels`.
    Confirm an initial changed response can return 200 and a subsequent
    unchanged response can return 304.
-   [ ] Leave the dashboard visible and confirm it refreshes at
    approximately the configured interval.
-   [ ] Hide the tab, wait, then return and confirm polling resumes
    appropriately.
-   [ ] Test the dashboard at phone width and confirm task actions are
    usable without horizontal scrolling.
-   [ ] Open Sales Orders, choose **Unpaid or part-paid**, and confirm
    only outstanding orders appear.
-   [ ] Move between pages and confirm the unpaid filter is preserved.
-   [ ] Confirm a user without payment-view permission cannot activate
    the filter by editing the URL.

### Scope of the recorded testing

The recorded verification covered the full automated test suite, seeded
PostgreSQL data, headless Chromium at desktop and phone widths, and the
refresh script's main paths, including automatic timer execution.

The following were **not** verified as part of that test run:

-   the farm's real production data;
-   physical mobile devices; and
-   the live Vercel deployment.

The deployed dashboard should therefore be checked on an actual phone
and against the live environment before treating the verification as
complete.

## 13. Deployment and versioning notes

The dashboard stylesheet cache version was advanced so browsers would
fetch the updated styles rather than continue using an older cached
file. The dashboard script also has a version query parameter for the
same general cache-busting purpose.

After deployment, verify that the live application serves the expected
templates, JavaScript and CSS. If a visual change does not appear, check
the asset version and browser cache before assuming the server-side code
failed to deploy.

The work was associated with the commit message:

`Add operational dashboard with live refresh`

The recorded test results describe the tested development environment;
they should not be interpreted as proof that the live deployment or real
production data has been tested.

## 14. Known follow-up work

At the time this documentation was prepared, two items remained outside
this dashboard implementation:

-   **Step 6b:** decide whether to include the role guide on the user
    form.
-   **Step 10:** complete the final round of tests and documentation
    updates.

These are separate follow-up tasks and should not be treated as
dashboard features already delivered.
