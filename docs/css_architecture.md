# CSS architecture

All styling is plain hand-written CSS in `static/css/`. There is no build step:
`templates/base/styles.html` links the shared files in cascade order, and a page
that needs its own styles loads one more file from `{% block extra_css %}`.

```text
static/css/
  base/
    tokens.css          every colour, radius, shadow, font and spacing value (light + dark)
    base.css            @font-face, reset, typography, focus ring, icon class, helpers
  layout/
    shell.css           navbar, sidebar / mobile drawer, main area, footer, page header
  components/
    buttons.css         .button + variants, .icon-button, .action-links
    cards.css           <section> / .card, <dl>, plain lists in cards, .auth-card
    tables.css          table presentation AND the "cards" presentation
    forms.css           .form-card, inputs, errors, fieldsets, .form-actions
    feedback.css        flash messages, badges, empty states
    navigation.css      filter tabs, pagination
    preferences.css     display-preferences dialog, segmented control
  pages/                loaded only by the page that needs them
    field-board.css     Crop Timeline        (crops/field_board.html)
    dashboard.css       Dashboard            (dashboard/dashboard.html)
```

## Rules of thumb

1. **Never write a raw colour outside `tokens.css`.** Use `var(--color-...)`.
   That is what lets the dark theme work: it only overrides tokens.
2. **Reusable things go in `components/`; one-page things go in `pages/`.**
3. **Adding or renaming a stylesheet:** edit `templates/base/styles.html`, and
   bump its single `v="..."` value whenever any CSS changes (browser cache).
4. **Specificity:** `main section` is deliberately weak (0,0,2) so any class can
   override it. Component classes live at (0,1,0); avoid IDs and `!important`.

## Themes and display preferences

* `static/js/prefs-init.js` is loaded in `<head>` and sets, before first paint:
  `data-theme="light|dark"` and the class `stack-tables` on `<html>`.
* Choices (`farm.theme`, `farm.lists`) are stored in the browser's
  `localStorage` and edited from the navbar's sliders button
  (`templates/base/prefs_dialog.html`, `static/js/prefs.js`).
* To add a theme-aware colour: define it in **both** the `:root` and
  `:root[data-theme="dark"]` blocks of `tokens.css`, then use the variable.
* No JavaScript means the light theme and ordinary scrolling tables.

## Tables on small screens

Markup stays `<div class="table-scroll"><table>...`. `static/js/tables.js`
copies each `<th>` text into every cell as `data-label`; when `stack-tables` is
set, `tables.css` renders each row as a card. The first column becomes the
card title and a column headed "Action(s)" becomes the button row.

## Buttons

Primary `.button` | tonal `.button-secondary` | quiet red `.button-danger`
(row-level Delete) | loud red `.button-danger.button-solid` (only the final
"Yes, delete" confirmation) | outline `.button-ghost` | compact `.button-small`.
Both `<a class="button">` and `<button>` get the same look and 44px touch
targets on touch screens.

## Icons

After using a new `icon="name"` in a template, run
`python tools/subset_icons.py` (needs `pip install fonttools brotli`) and
commit the regenerated font in `static/fonts/material-symbols/`.
