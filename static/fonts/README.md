# Locally hosted fonts

These assets are served by Django from `static/fonts/`; the application does
not request either font from Google at runtime.

## Inter

- `inter/inter-latin.woff2` and `inter/inter-latin-ext.woff2` are the Inter
  variable WOFF2 subsets for weights 400–700, distributed by Google Fonts
  (Inter v20).
- Upstream family: [Google Fonts Inter](https://github.com/google/fonts/tree/main/ofl/inter)
- License: SIL Open Font License 1.1; see [inter/OFL.txt](./inter/OFL.txt).

## Material Symbols Outlined

- `material-symbols/material-symbols-outlined.woff2` is Google's variable
  Outlined font, from the
  [official Material Design Icons repository](https://github.com/google/material-design-icons/tree/master/variablefont).
- License: Apache License 2.0; see
  [material-symbols/LICENSE.txt](./material-symbols/LICENSE.txt).

The existing `STATICFILES_DIRS` configuration includes these files for
development and `collectstatic` deployment builds.
