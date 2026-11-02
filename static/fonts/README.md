# Locally hosted fonts

These assets are served by Django from `static/fonts/`; the application does
not request either font from Google at runtime.

## Inter

- `inter/inter-latin.woff2` and `inter/inter-latin-ext.woff2` are the Inter
  variable WOFF2 subsets for weights 400–700, distributed by Google Fonts
  (Inter v20).
- Upstream: [official Material Design Icons repository](https://github.com/google/material-design-icons/tree/master/variablefont).
- License: Apache License 2.0; see
  [material-symbols/LICENSE.txt](./material-symbols/LICENSE.txt).

## Material Symbols Outlined (subset)

- `material-symbols/material-symbols-subset.woff2` is a **generated** font that
  contains only the icons the templates use (a few KB instead of ~4 MB). Do not
  edit it by hand. `material-symbols/icons.txt` lists the icons it contains.
- It is built from Google's variable Outlined font (kept in
  `tools/material-symbols-outlined.full.woff2`, outside `static/`) by
  `tools/subset_icons.py`. When you use a new icon name in a template, run:

The existing `STATICFILES_DIRS` configuration includes these files for
development and `collectstatic` deployment builds.
