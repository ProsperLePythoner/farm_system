# Implementation Task: Farm System UI/UX Observations

## Objective

Address the actionable observations documented in `docs/observations.md` in the Farm System (Agribusiness Management System) repository.

Improve correctness, usability, accessibility, visual consistency, and mobile responsiveness without introducing unnecessary architectural complexity or disrupting existing functionality.

Treat `docs/observations.md` as the primary list of requirements, but inspect the current implementation before deciding how each requirement should be addressed.

## 1. Mandatory Working Rules

Before modifying anything:

1. Inspect `docs/observations.md` and the current repository structure.
2. Inspect the relevant models, forms, views, URL configurations, templates, shared template components, CSS, settings, and existing tests.
3. Trace each observation to its actual implementation. Do not assume that a feature is missing or broken merely because the observation describes it that way.
4. Check the working tree and current branch. Preserve all existing user changes, including uncommitted and untracked work. Never discard or overwrite unrelated changes.
5. Identify dependencies between tasks and implement them in a sensible order.

During implementation:

- Prefer targeted changes over broad refactoring.
- Follow existing Django conventions and the project's current architecture.
- Keep business logic in appropriate models, forms, services, or views rather than putting it in templates.
- Use server-side validation for all important business rules; JavaScript may improve the interface but must not replace server-side enforcement.
- Reuse existing styling conventions and installed dependencies where practical.
- Do not introduce React, a new CSS framework, a component library, or additional packages merely to complete these tasks.
- Do not change database models or create migrations unless the inspected implementation demonstrates that they are necessary.
- Do not introduce unrelated features, modify production data, or change deployment configuration without a demonstrated need.
- Write beginner-friendly code with clear naming and focused comments where they add value.

## 2. Phase One: Harvest Management Correctness

### 2.1 Display the planted quantity when recording a harvest

Investigate the planting and harvest models, forms, views, and templates.

When a user selects a planting record while registering a harvest, make the relevant planting quantity visible so the user does not need to remember or look it up separately.

Requirements:

- Display the relevant planted quantity and its unit, where available.
- Clearly associate the displayed quantity with the selected planting record.
- If planting records can be changed in the form, ensure the displayed information stays synchronized with the current selection.
- Provide a sensible fallback when the quantity is unavailable.
- Reuse existing fields and relationships instead of duplicating data unnecessarily.

Do not assume that the planted quantity and harvested quantity use the same unit.

### 2.2 Validate harvest quantities

Investigate the meaning, units, and relationships of the existing planting and harvest quantity fields before implementing a restriction.

If the quantities represent comparable measurements and the business rules establish an applicable limit, reject harvest records that exceed that limit.

Requirements:

- Perform validation on the server.
- Display a clear, field-associated validation message explaining the problem.
- Preserve the user's other valid form inputs when validation fails.
- Ensure invalid submissions do not create or partially save a harvest record.
- Check how multiple harvest records associated with the same planting should be handled. Do not incorrectly compare an individual harvest against the planted quantity if the intended rule concerns cumulative harvests.
- Prevent invalid values through direct POST requests as well as normal browser interaction.
- Add tests for valid quantities, boundary values, excessive quantities, and any relevant cumulative limits.

Important: If planted quantity and harvested quantity measure different things, such as plant count and kilograms of produce, do not compare them directly. Explain the issue and identify the appropriate business rule rather than introducing an invalid restriction.

## 3. Phase Two: Account Management

### 3.1 Identify superuser administrators

Inspect the existing account-management templates and the authenticated user's properties.

Make it immediately apparent when the current user is a Django superuser.

Requirements:

- Show a concise, visually distinct label such as "Superuser" or "Superuser administrator" in an appropriate location.
- Base the label on the actual server-provided superuser status, not a username or manually assigned display string.
- Keep the presentation consistent with the existing interface.
- Do not confuse Django's `is_superuser` flag with staff status, ordinary authentication, or application-specific roles.
- Do not alter permissions simply to display the label.

### 3.2 Correct the deactivate button's sizing

Inspect the existing deactivate action and its CSS.

Requirements:

- Reduce excessive padding, height, or width as appropriate.
- Keep the button comfortably clickable, legible, and consistent with other account-management actions.
- Preserve its existing behavior, URL, HTTP method, and permission checks.
- Check the result at both desktop and narrow viewport widths.

Do not make the button so small that it becomes difficult to use.

## 4. Phase Three: Order Management UX

### 4.1 Explain unit prices

Inspect the New Order form, its order-item formset, relevant forms, and templates.

Make the meaning of the unit price field explicit.

Requirements:

- Use a clear label such as "Unit price" and explanatory text such as "Price per unit of the selected harvest produce."
- Display the appropriate unit of measurement where the existing data model supports it.
- Clarify the relationship between quantity, unit price, and line total.
- Make it clear which price is entered by the user and which amounts are calculated automatically.
- Avoid displaying unexplained or duplicated price information.
- Preserve existing pricing rules and server-side calculations.

Do not introduce a new pricing model or assume a currency that the application has not established.

### 4.2 Clarify the order-item delete action

Inspect the existing behavior of the Delete button beside each order item.

Determine whether it removes an unsaved form row, deletes a persisted order item, or performs another operation.

Requirements:

- Give the action an explicit label, such as "Remove item," where appropriate.
- Make it clear which item will be removed.
- If removal happens immediately, provide an appropriate confirmation when necessary and preserve normal form behavior.
- For Django formsets, correctly maintain the required management fields, indices, and deletion fields.
- Ensure that removing one row does not accidentally remove or corrupt other rows.
- Preserve server-side authorization and validation.
- If the item has already been saved, distinguish removal from deletion of the entire order and handle the associated business rules safely.
- Test removing the first, middle, and last item, as well as submitting the form after removing an item.

Do not merely rename the button without verifying what it actually does.

### 4.3 Improve numerical readability

Make monetary amounts and relevant large numerical values easier to scan.

Requirements:

- Apply consistent thousands separators to displayed values where appropriate.
- Apply formatting to order totals, line totals, unit prices, payments, and outstanding balances where those values appear.
- Preserve the underlying numerical values and calculations.
- Do not convert monetary values into strings before arithmetic.
- Preserve decimal precision and trailing decimal places according to the existing currency and pricing conventions.
- Handle empty, null, and zero values sensibly.
- Prefer Django's existing template formatting facilities or a small reusable formatter over duplicated formatting logic.

Check whether Django's `humanize` application is already installed before considering changes to settings.

## 5. Phase Four: Consistent UI and Mobile Responsiveness

### 5.1 Audit shared styling first

Inspect the shared base template, navigation, existing stylesheets, and representative pages from the crops, harvests, customers, sales, accounts, and dashboard applications.

Identify the smallest reusable changes that will improve consistency across the application.

Requirements:

- Standardize common button styles, spacing, form controls, headings, tables, and feedback messages.
- Preserve clear visual distinctions between primary, secondary, destructive, and disabled actions.
- Keep labels, help text, validation errors, and empty states readable.
- Reuse shared components and CSS classes where practical.
- Avoid introducing different styling systems for individual applications without a clear reason.

### 5.2 Improve mobile responsiveness

Inspect tables, forms, navigation, typography, and action links at narrow viewport widths.

Requirements:

- Prevent page-wide horizontal overflow where reasonably possible.
- Make forms and form controls fit available screen space.
- Keep buttons and links usable on touchscreens.
- Allow tables to adapt appropriately, using responsive layouts or contained horizontal scrolling when necessary.
- Ensure long values and action groups do not break the layout.
- Maintain readable typography and sensible spacing without unnecessarily shrinking text.
- Preserve access to every important action on mobile.

Do not hide important business information or functionality merely to make a page fit.

### 5.3 Add meaningful icons

Add relevant icons to action links where they improve recognition and usability.

Requirements:

- Inspect existing icon support before adding anything new.
- Prefer an existing icon library or project assets if already available.
- Use consistent icon sizing and spacing.
- Ensure destructive actions remain distinguishable from ordinary navigation.
- Provide accessible names for icon-only controls; decorative icons should not create redundant screen-reader announcements.
- Retain visible text alongside icons wherever practical.
- Do not add an external dependency solely for decorative icons unless genuinely necessary.

## 6. Explicitly Deferred Features

The following observations are future requirements, not part of this implementation:

- A harvest calendar.
- Email reminders for approaching expected harvest windows.
- Optional light and dark display themes.

Do not build these features in this task. Preserve the observations in `docs/observations.md` and, if appropriate, add concise implementation notes or a separate future-work document explaining their dependencies.

In particular, do not implement email reminders by merely sending messages on every page request. A future notification feature will require a reliable scheduling mechanism, appropriate date-window logic, and duplicate-notification prevention.

## 7. Testing and Verification

Before finishing:

1. Run the relevant existing Django tests.
2. Add or update tests for the new validation rules, form behavior, order-item removal, and other meaningful server-side changes.
3. Check template rendering and URL resolution for the affected pages.
4. Run Django system checks where the local environment supports them.
5. Verify that valid existing workflows continue to work.
6. Review the changes for unintended modifications, duplicated logic, accessibility regressions, and inconsistent formatting.
7. If browser testing is available, inspect representative pages at desktop and mobile viewport widths.

If the database, environment variables, dependencies, or other local requirements prevent a check from running, report that limitation explicitly. Never claim a test passed unless it actually ran successfully.

## 8. Acceptance Criteria

The task is complete when:

- [ ] The planted quantity is visible when recording a harvest.
- [ ] Harvest quantity restrictions reflect valid business rules and are enforced server-side.
- [ ] Superuser administrators are clearly identified.
- [ ] The deactivate button is appropriately sized.
- [ ] Unit prices and calculated order amounts are clearly explained.
- [ ] The order-item removal action communicates its purpose and behaves correctly.
- [ ] Monetary amounts use consistent, readable numerical formatting.
- [ ] Shared UI styling is more consistent.
- [ ] Important pages and tables are usable on mobile screens.
- [ ] Relevant action links have meaningful, accessible icons where appropriate.
- [ ] Existing workflows and permissions remain intact.
- [ ] Relevant tests and checks have been executed and their results reported.
- [ ] Calendar, email reminders, and theme switching remain deferred.

## 9. Final Report

Provide a concise implementation report containing:

1. **Changes made:** Grouped by phase and observation.
2. **Files changed:** List the important files and explain why each changed.
3. **Business-rule decisions:** Explain how harvest quantity validation was determined and any assumptions that remain.
4. **Tests and checks:** List each command or check executed and whether it passed.
5. **Outstanding issues:** Identify blocked work, unresolved ambiguities, and deferred requirements.
6. **Migration and dependency impact:** State whether migrations or new packages were required.
7. **Manual verification:** Identify anything that still needs a human to inspect in the browser.

Do not mark unfinished work as complete. Do not commit, push, deploy, or modify production data unless explicitly authorized.

Begin with repository inspection, then implement the phases in order. If a critical business rule cannot be established from the existing code or documentation, explain the uncertainty before making a potentially incorrect change.