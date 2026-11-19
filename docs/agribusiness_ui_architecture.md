# Agribusiness UI Architecture and Improvements

**Purpose:** Document the UI redesign, explain how its parts work
together, and establish guidelines for future maintenance.

**Scope:** Shared application styling, design tokens, light/dark themes,
display preferences, responsive tables, typography and icons, the
Dashboard, and the Crop Timeline.

------------------------------------------------------------------------

## 1. Overview

The redesign replaces a large, centralised stylesheet with a layered UI
architecture. Each part now has a clearer responsibility:

1.  **Design tokens** define the shared visual language.
2.  **Component stylesheets** define reusable controls and interface
    elements.
3.  **Layout stylesheets** define the shared application shell.
4.  **Page stylesheets** define page-specific presentation.
5.  **Preference scripts** apply user-selected display settings.
6.  **Django templates and views** provide page structure and data
    without becoming the source of global styling decisions.

The goal is a more consistent, responsive, accessible, and maintainable
interface without changing the farm-management domain model.

## 2. Stylesheet architecture

The redesigned structure is organised by responsibility:

``` text
static/css/
├── base/
│   ├── base.css
│   └── tokens.css
├── components/
│   ├── buttons.css
│   ├── cards.css
│   ├── feedback.css
│   ├── forms.css
│   ├── navigation.css
│   ├── preferences.css
│   └── tables.css
├── layout/
│   └── shell.css
└── pages/
    ├── dashboard.css
    └── field-board.css
```

### `base/tokens.css` --- design tokens

This is the central source of shared visual values. It defines CSS
custom properties for:

-   Brand colours and primary actions.
-   Page, card, input, and secondary surfaces.
-   Main, secondary, and tertiary text.
-   Form-control borders and interaction states.
-   Button variants, including secondary and danger styles.
-   Navigation colours and states.
-   Status colours and status-chip pairs.
-   Feedback-message colours.
-   Dashboard and timeline helper colours.
-   Chart and data-visualisation colours.
-   Radii, shadows, font stacks, type sizes, spacing, and touch-target
    sizing.

The light theme is defined on `:root`. The dark theme overrides colour
tokens under `:root[data-theme="dark"]`. Most geometry and typography
are inherited, so theme switching does not require duplicating the
entire stylesheet.

**Maintenance rule:** Look for an existing token before introducing a
new hard-coded colour or visual value.

### `base/base.css` --- foundation

Provides the base CSS layer and works with the token, component, layout,
and page stylesheets.

### `components/` --- reusable elements

  -----------------------------------------------------------------------
  Stylesheet                          Responsibility
  ----------------------------------- -----------------------------------
  `buttons.css`                       Shared button appearance and
                                      variants

  `cards.css`                         Reusable cards and panels

  `feedback.css`                      Success, warning, error,
                                      informational, and message states

  `forms.css`                         Form controls, labels, and related
                                      styling

  `navigation.css`                    Shared navigation elements and
                                      states

  `preferences.css`                   Display-preferences dialog and
                                      controls

  `tables.css`                        Tables and responsive table-to-card
                                      presentation
  -----------------------------------------------------------------------

If a component is shared across multiple pages, its styling belongs
here. Avoid copying shared component rules into individual page
stylesheets.

### `layout/shell.css` --- application structure

Owns the larger shared layout regions, including navigation, sidebar,
and main-content placement.

### `pages/` --- page-specific presentation

  -----------------------------------------------------------------------
  Stylesheet                          Page
  ----------------------------------- -----------------------------------
  `dashboard.css`                     Farm Dashboard

  `field-board.css`                   Crop Timeline (internally referred
                                      to as the field board)
  -----------------------------------------------------------------------

Page stylesheets should contain only rules specific to their page.

------------------------------------------------------------------------

## 3. Theme system

The interface supports light and dark themes through the same
design-token system.

### Light theme

The light theme is the default fallback. It uses a pale page background,
white primary surfaces, subtle borders, dark readable text, and green
brand/primary-action colours.

### Dark theme

The dark theme uses dark slate surfaces, lighter text, adjusted borders,
and theme-specific navigation, form-control, status-chip, feedback,
shadow, and chart colours.

The active theme is represented on the root HTML element:

-   `data-theme="light"`
-   `data-theme="dark"`

### Semantic colour usage

Colours should communicate meaning consistently:

-   Green: farm identity, primary actions, growth, and success.
-   Amber: upcoming or open-window attention states.
-   Coral/red: missed or error states.
-   Blue: recorded events and data visualisation.
-   Other chart colours: distinguish datasets.

Do not rely on colour alone to communicate status. Keep labels, markers,
or other visual cues.

------------------------------------------------------------------------

## 4. Display preferences

The redesign adds a **Display preferences** dialog, allowing users to
control how the interface is presented.

### Theme

Users can choose:

-   **System** --- follow the device/browser colour preference.
-   **Light** --- always use the light theme.
-   **Dark** --- always use the dark theme.

### Lists and tables

Users can choose:

-   **Auto** --- cards on smaller screens and tables on larger screens.
-   **Table** --- prefer the tabular presentation.
-   **Cards** --- prefer the card presentation.

Preferences are stored in the current browser using `localStorage`. They
are device/browser-specific, not Django account settings.

### Relevant files

``` text
templates/base/prefs_dialog.html
static/js/prefs-init.js
static/js/prefs.js
static/css/components/preferences.css
```

`prefs-init.js` is loaded in the document head before the page is
painted. This applies the saved theme and list layout early and prevents
a visible flash of the wrong theme.

The script:

-   Reads and validates stored preference values.
-   Falls back to `auto` if values are missing, invalid, or storage is
    unavailable.
-   Resolves System theme using `prefers-color-scheme`.
-   Resolves Auto list layout using the viewport width.
-   Applies `data-theme` to the root element.
-   Applies the `stack-tables` class when card-style tables should be
    shown.
-   Exposes `window.FarmPrefs.get()` and `window.FarmPrefs.set()`.

`prefs.js` opens the dialog, synchronises its controls with saved
settings, and applies changes immediately. There is no separate Save
button.

### Maintenance considerations

-   Keep allowed values consistent between the JavaScript and dialog
    controls.
-   Keep `prefs-init.js` early in the document head; moving it to the
    page bottom can reintroduce theme flashing.
-   Treat local storage as optional.
-   When changing a preference, update its key, validation, controls,
    and documentation together.

------------------------------------------------------------------------

## 5. Responsive tables and lists

The list-layout preference supports different presentations for
different devices.

In Auto mode, smaller screens use a stacked/card presentation while
larger screens retain conventional tables. The preference script
controls this through the `stack-tables` class on the root HTML element,
and the table component stylesheet responds to that class.

This centralises the layout decision instead of requiring each list page
to implement its own screen-width logic.

New list pages should follow the shared table/list conventions so they
can participate in the same responsive behaviour.

------------------------------------------------------------------------

## 6. Typography and icon assets

The shared template preloads local font assets:

``` text
static/fonts/inter/inter-latin.woff2
static/fonts/material-symbols/material-symbols-subset.woff2
```

The design tokens define Inter as the preferred interface font, with
system fonts as fallbacks. The Material Symbols subset supplies the
interface icons without requiring the full icon font.

When introducing a new Material Symbol:

1.  Check whether it is already in the subset.
2.  If missing, update the subset using `tools/subset_icons.py`.
3.  Verify it in the browser.
4.  Avoid adding a full external icon library for only a few icons.

------------------------------------------------------------------------

## 7. Shared template integration

The shared base template connects global assets and reusable interface
elements:

-   Early preference initialisation.
-   Preloaded local font and icon assets.
-   Shared stylesheet inclusion through `templates/base/styles.html`.
-   Navbar, sidebar, footer, and navigation backdrop.
-   Display-preferences dialog.
-   Preference and table JavaScript modules.
-   Page-specific CSS and JavaScript through template blocks.

The Dashboard and Crop Timeline load their own stylesheets through the
`extra_css` block. This keeps page-specific styling separate from global
styles.

New pages should use the shared base template rather than duplicating
the application shell.

------------------------------------------------------------------------

## 8. Dashboard and Crop Timeline

### Farm Dashboard

The Dashboard has a dedicated stylesheet:

``` text
static/css/pages/dashboard.css
```

Dashboard-specific presentation belongs here. Shared cards, buttons,
navigation, and feedback should continue to use their component
stylesheets and design tokens.

### Crop Timeline

The Crop Timeline has a dedicated stylesheet:

``` text
static/css/pages/field-board.css
```

The page includes:

-   Production overview header.
-   Summary statistics.
-   Search and filtering controls.
-   Planting timeline grouped by field.
-   Crop identifiers and growth bars.
-   Harvest-window markers and recorded-harvest dots.
-   Status labels.
-   Crop-mix visualisation.
-   Weekly harvest-activity chart.
-   Supporting details and harvest-recording links.

The page stylesheet uses shared tokens for text, surfaces, borders,
shadows, status colours, and other visual values. It also includes
responsive rules for smaller screens. The timeline can scroll
horizontally when its time axis requires more width than a phone
provides; supporting panels and statistics adapt to narrower viewports.

Timeline geometry belongs in the page stylesheet. Global colour
decisions belong in `tokens.css`.

------------------------------------------------------------------------

## 9. Crop Timeline colour refinement identified for follow-up

A later review identified an opportunity to improve dark-theme data
visualisation.

The Django view in `apps/crops/views.py` defines a deterministic crop
palette. It hashes the crop name and selects a colour from a fixed
palette. This gives a crop a stable colour without storing presentation
data in the database.

The review found that several colours in the existing palette are muted
green/brown tones and can blend into the dark theme.

The design tokens already include:

``` css
--chart-blue
--chart-teal
--chart-purple
--chart-amber
--chart-coral
--chart-activity-start
--chart-activity-end
```

The weekly activity chart also has a green `--bar-gradient` despite the
dedicated activity-gradient tokens.

### Proposed refinement

The proposed direction is to:

-   Retain deterministic crop-colour assignment.
-   Use the existing chart palette for crop identifiers and chart
    segments.
-   Use the activity-gradient tokens for weekly activity bars.
-   Make dark timeline tracks and grid lines more neutral slate.
-   Improve contrast for muted pills and links where necessary.
-   Preserve semantic status colours and the light theme's visual
    identity.

**Status:** This is a proposed follow-up from the design review, not a
confirmed completed change. Mark it complete only after applying the
changes and checking the rendered page in both themes.

A hash-modulo palette can occasionally assign the same colour to
different crop names. If the number of crops makes this confusing, a
future improvement could minimise collisions within the active crop set
while preserving stable assignments. That is a separate design decision.

------------------------------------------------------------------------

## 10. File responsibility reference

  ------------------------------------------------------------------------
  File or directory                    Responsibility
  ------------------------------------ -----------------------------------
  `static/css/base/tokens.css`         Shared design tokens and theme
                                       overrides

  `static/css/base/base.css`           CSS foundation

  `static/css/components/`             Reusable interface component styles

  `static/css/layout/shell.css`        Shared application layout

  `static/css/pages/dashboard.css`     Dashboard-specific styling

  `static/css/pages/field-board.css`   Crop Timeline-specific styling

  `templates/base/styles.html`         Shared stylesheet inclusion

  `templates/base/prefs_dialog.html`   Display-preferences dialog markup

  `static/js/prefs-init.js`            Early preference loading and
                                       application

  `static/js/prefs.js`                 Preferences dialog interaction

  `static/js/tables.js`                Responsive table/list behaviour

  `templates/base/base.html`           Shared template integration

  `apps/crops/views.py`                Crop Timeline data preparation and
                                       crop-colour assignment

  `templates/crops/field_board.html`   Crop Timeline markup and data
                                       presentation
  ------------------------------------------------------------------------

------------------------------------------------------------------------

## 11. Maintenance guidelines

### Where should a change go?

  Change                                    Correct location
  ----------------------------------------- --------------------------------
  Global colour, radius, or shadow          `tokens.css`
  Shared button                             `components/buttons.css`
  Shared card                               `components/cards.css`
  Shared form control                       `components/forms.css`
  Shared navigation                         `components/navigation.css`
  Shared table/card-list behaviour          `components/tables.css`
  Application shell layout                  `layout/shell.css`
  Dashboard-only layout                     `pages/dashboard.css`
  Crop Timeline-only layout                 `pages/field-board.css`
  Theme or list preference behaviour        `prefs-init.js` and `prefs.js`
  Crop Timeline data or colour assignment   `apps/crops/views.py`

### Practical rules

1.  **Look for an existing token first.** Avoid scattering new
    hexadecimal colours through page stylesheets.
2.  **Keep shared components shared.** Do not copy button, card, form,
    or table rules into individual pages.
3.  **Keep page-specific layout local.** Timeline geometry belongs in
    the Crop Timeline stylesheet.
4.  **Separate presentation from business logic.** Crop colours are
    presentation data; they should not become database fields without a
    clear product requirement.
5.  **Preserve semantic states.** A status colour should mean the same
    thing wherever that status appears.
6.  **Check both themes.** A change that works in light mode may fail
    against dark surfaces.
7.  **Check narrow screens.** Verify phone widths and intentional
    horizontal scrolling.
8.  **Check keyboard interaction.** Dialogs, controls, links, and
    scrollable regions should remain usable without a mouse.
9.  **Check contrast.** Do not assume a colour pair is accessible merely
    because it looks readable on one display.
10. **Update cache versions when needed.** If static assets are
    versioned in template URLs, update the relevant version after
    changing those assets.
11. **Avoid unnecessary JavaScript.** Prefer CSS for visual behaviour;
    use JavaScript when interaction or preferences require it.
12. **Preserve fallbacks.** The light theme and ordinary page structure
    should remain usable if preference JavaScript does not run.

------------------------------------------------------------------------

## 12. Verification checklist

After UI changes, verify the following in a local browser.

### Themes

-   [ ] Light theme renders correctly.
-   [ ] Dark theme renders correctly.
-   [ ] System theme follows the device preference.
-   [ ] Saved theme is applied before the page visibly renders.
-   [ ] Text, borders, inputs, badges, and feedback messages remain
    readable.

### Display preferences

-   [ ] Preferences dialog opens and closes.
-   [ ] Theme changes apply immediately.
-   [ ] List-layout changes apply immediately.
-   [ ] Preferences persist after a page reload.
-   [ ] Invalid or unavailable local storage does not break the page.

### Responsive layout

-   [ ] Tables use the expected desktop presentation.
-   [ ] Auto mode uses cards on smaller screens.
-   [ ] Manual Table and Cards preferences work.
-   [ ] Navigation and content remain usable on narrow screens.
-   [ ] Timeline scrolling works on touch devices.

### Page-specific checks

-   [ ] Dashboard cards and layout use the shared design system.
-   [ ] Crop Timeline statistics and filters remain aligned.
-   [ ] Timeline bars, markers, and recorded-harvest dots are
    distinguishable.
-   [ ] Crop-mix and activity charts remain readable in both themes.
-   [ ] Empty states and long crop/field names do not break the layout.

### General checks

-   [ ] No missing font or icon assets.
-   [ ] No browser-console errors from preference scripts.
-   [ ] No unexpected horizontal overflow outside intentionally
    scrollable regions.
-   [ ] Django pages, links, and forms still work.
-   [ ] Run the relevant automated tests after visual changes.

------------------------------------------------------------------------

## 13. Architectural summary

The redesigned UI follows a layered structure:

1.  **Tokens** define the visual language.
2.  **Components** turn that language into reusable interface elements.
3.  **Layout** arranges the shared application shell.
4.  **Page stylesheets** handle page-specific composition.
5.  **Preference scripts** let users choose how the interface is
    presented.
6.  **Django templates and views** provide structure and data without
    taking over the global design system.

The key maintenance principle is to preserve these boundaries. Make a
change at the narrowest layer that owns it, while allowing shared visual
decisions to flow from the design tokens.
