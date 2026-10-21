# Task: UI Polish — Local Fonts and Icons

**Project:** Agribusiness Management System (`farm_system`)  
**Branch:** `improve/ui-ux`  
**Priority:** Visual consistency and usability  
**Scope:** Typography, iconography, and minor visual refinements only

## 1. Objective

Improve the application's visual polish by introducing:

- **Inter** as the primary interface font.
- **Google Material Symbols Outlined** as the consistent icon system.
- Locally hosted font assets served through Django static files.
- Subtle improvements to typography, navigation alignment, spacing, and interaction states.

The result should feel like a clean, modern agricultural management dashboard while preserving the existing forest-green identity and established Django architecture.

**Important:** Mobile responsiveness will be addressed in a separate task. Do not attempt a full responsive redesign here.

## 2. Preflight: protect existing work

Before making changes:

1. Verify that you are in the correct `farm_system` repository.
2. Inspect the current Git state:
   - `git status --short --branch`
   - `git branch --show-current`
   - `git branch --list`
3. Confirm that the active branch is `improve/ui-ux`.
4. Inspect any uncommitted changes. Do not overwrite, discard, reset, or silently reorganize existing work.
5. If the branch is missing or the working tree presents a risk, stop and report the issue before proceeding.

Do not commit, push, merge, tag, or deploy. The changes must remain available for the user to review.

## 3. Inspect the existing implementation

Read the relevant templates, stylesheets, and static-file configuration before editing. Confirm the current paths rather than assuming they have not changed.

Inspect these shared components first:

- `templates/base/base.html`
- `templates/base/navbar.html`
- `templates/base/sidebar.html`
- `templates/base/footer.html`
- `static/css/base.css`
- `static/js/shell.js`

Also inspect the relevant page templates before deciding where action icons would be useful.

Preserve existing Django template blocks, URL names, permission checks, active-navigation behavior, form functionality, and responsive foundations.

## 4. Self-host the Inter font

Use **Inter** as the primary UI font.

### Requirements

1. Obtain the font from an authoritative source, preferably the official Google Fonts repository.
2. Verify its licence and retain any required licence or attribution notice.
3. Store the required font files in a clear directory, such as:

   `static/fonts/inter/`

4. Prefer WOFF2 for web delivery. Include only the weights and files actually needed.
5. Configure the font using `@font-face` in the existing stylesheet or a small dedicated stylesheet.
6. Set `font-display: swap` and provide sensible fallback fonts.
7. Apply the font consistently to the main application interface without making data-dense screens harder to read.
8. Reference the local files through Django's static-file conventions.

**Do not load Inter through a remote Google Fonts stylesheet or request the font from Google's servers at runtime.**

If the environment cannot retrieve the font asset, report the limitation and identify the verified source and required files. Do not substitute a remote font link and claim the task is complete.

## 5. Self-host Material Symbols Outlined

Use **Google Material Symbols Outlined** as the application's primary icon family.

### Requirements

1. Obtain the icon font from an authoritative source, preferably Google's official Material Symbols repository or distribution.
2. Verify the applicable licence and retain any required notice.
3. Store the font locally, for example:

   `static/fonts/material-symbols/`

4. Configure the font using a local `@font-face` declaration.
5. Do not load Google's icon stylesheet or font files from a remote server at runtime.
6. Create a reusable CSS class for icons, with consistent sizing, alignment, line height, and spacing.
7. Use Material Symbols ligature names in the templates rather than duplicating styling for individual icons.
8. Avoid downloading unnecessary formats or duplicate font files.

Suggested icon names to verify against the official icon set:

| Purpose | Suggested symbol |
|---|---|
| Dashboard | `dashboard` |
| Crops | `grass` |
| Fields or agricultural operations | `agriculture` |
| Plantings | `event_available` |
| Harvests | `agriculture` or another suitable harvest-related symbol |
| Customers | `people` |
| Sales | `point_of_sale` |
| User accounts | `manage_accounts` |
| Add/create | `add` |
| Edit | `edit` |
| Delete | `delete` |
| Logout | `logout` |
| Navigation menu | `menu` |

Select symbols based on their actual meaning. Avoid using the same icon everywhere simply for visual consistency.

### Accessibility

- Mark decorative icons with `aria-hidden="true"`.
- Preserve visible text alongside navigation icons.
- Give icon-only buttons accessible names, such as an appropriate `aria-label`.
- Maintain visible keyboard focus indicators.
- Ensure the interface remains understandable if the icon font fails to load.

A local icon font is sufficient for this task. Do not create individual SVGs for every icon unless the existing architecture or a specific accessibility requirement justifies doing so.

## 6. Improve typography and visual consistency

Make restrained refinements to the existing shared stylesheet.

### Typography

Establish a consistent hierarchy for:

- Page titles
- Section headings
- Form labels
- Body text
- Table headings and data
- Helper text and secondary information
- Buttons and navigation labels

Use existing CSS variables where possible. Introduce a small set of typography variables only where they improve consistency.

Keep font sizes, weights, line heights, and spacing practical for a management application. Avoid excessive decorative typography.

### Navigation

Add appropriate icons to the existing sidebar links where they improve recognition.

Preserve:

- Existing visible link labels
- Django URL names and destinations
- Permission checks
- Active-page indicators
- Current navigation behavior

Align icons consistently with their text. Do not convert the sidebar into icon-only navigation.

Inspect the navbar and add or adjust icons only where they provide a clear benefit.

### General appearance

Preserve the current forest-green identity and layout. Where useful, make small refinements to:

- Icon and label alignment
- Spacing between related elements
- Border consistency
- Hover states
- Focus states
- Heading and section spacing

Do not redesign every page merely for uniformity. Prioritize the shared shell, then make limited changes to individual pages where the improvement is clear.

## 7. Static-file and offline considerations

The fonts and icons must be served from the application's own static assets.

Check the project's existing Django static-file configuration and follow its conventions. Do not change deployment configuration unnecessarily.

Remember that locally hosted assets only eliminate the need to contact Google for those assets. Other application features may still require an internet connection.

If the project uses a static-file collection or deployment pipeline, verify that the new font files will be included by the existing setup.

## 8. Scope boundaries

### Included

- Local Inter font files and configuration
- Local Material Symbols font files and configuration
- Small shared-shell styling improvements
- Sidebar icon integration
- A limited number of useful action icons
- Necessary asset licence notices and concise documentation

### Excluded

- Full mobile-responsiveness redesign
- Major template restructuring
- Changes to Django models, views, URLs, permissions, or business logic
- Changes to form validation or database behavior
- React, Tailwind, Bootstrap, or another new frontend framework
- Theme switching, calendar features, email reminders, or unrelated functionality
- Git commits, pushes, merges, tags, or deployments

If you discover a necessary change outside this scope, explain why before expanding the task.

## 9. Validation and review

After implementation:

1. Run `python manage.py check` using the project's configured environment.
2. Run relevant existing tests where practical.
3. Verify that changed Django templates remain syntactically valid.
4. Confirm that all existing URLs, permission checks, and active-navigation conditions are preserved.
5. Confirm that font and icon assets are loaded from local static paths.
6. Search the changed templates and stylesheets for accidental remote Google Fonts dependencies.
7. Verify that fallback fonts are defined and that navigation text remains meaningful without icons.
8. Check that icon ligatures render correctly and do not display raw symbol names under normal conditions.
9. Review keyboard focus states, contrast, and accessible names for interactive controls.
10. Inspect the final Git diff and remove unrelated changes, unused styles, and duplicate assets.
11. Confirm that the active branch remains `improve/ui-ux` and report the final Git status.

If a check cannot run because of missing dependencies, unavailable assets, or environment configuration, state the exact reason. Never report a test as passed unless it was actually run successfully.

## 10. Completion report

Provide a concise report containing:

- The verified branch name
- Files changed or added, with their purpose
- Local font and icon asset paths
- Verified asset sources and licence handling
- Where typography and icons were applied
- Checks and tests actually run, including their results
- Any unresolved limitations or required manual steps
- Final Git status

Explicitly state that the full mobile-responsiveness pass remains outstanding.

## Acceptance criteria

- [ ] Inter is served from local project assets.
- [ ] Material Symbols Outlined is served from local project assets.
- [ ] No runtime Google Fonts requests are needed for these assets.
- [ ] Font licensing and attribution requirements are handled appropriately.
- [ ] Typography is consistent and readable.
- [ ] Sidebar icons are meaningful, aligned, and consistently styled.
- [ ] Existing link text, routes, permissions, and active states remain intact.
- [ ] Existing application functionality and branding are preserved.
- [ ] The diff is focused and reviewable.
- [ ] No commit, push, merge, tag, or deployment has occurred.
- [ ] Mobile responsiveness remains a separate, future task.
