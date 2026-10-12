# Documentation Notes

This file records confirmed gaps or mismatches found while documenting the
current checkout. It is not a request to change business behavior as part of the
documentation work.

## Confirmed mismatches and open questions

- **Harvest window wording:** `README.md` says the end is the start plus three
  days. `Planting.harvest_end` is `harvest_start + 2 days`, making a three-day
  inclusive window. The code and the model documentation were followed; the
  main README was intentionally not edited.
- **Role/access documentation is stale:** `docs/roadmap.md` and
  `docs/view_architecture.md` say role-based access is not implemented. The
  current code defines five role groups in `apps/accounts/roles.py`, a
  `setup_roles` command, and server-side permission checks. The dashboard is
  role-gated but remains a permission-filtered navigation page; operational
  metrics and role-specific dashboard data are not implemented.
- **Deployment checklist status is stale:** the deployment checklist says
  “Planning / Phase 1 not yet verified,” while the README and project
  configuration describe a Vercel deployment. The checklist should be checked
  against the actual deployment before being treated as current.
- **Tailwind dependency residue:** `requirements.txt` still includes
  `django-tailwind` and `pytailwindcss`; Tailwind is not in `INSTALLED_APPS` and
  the current templates do not load Tailwind. `docs/roadmap.md` says the
  integration was removed, which does not explain why those packages remain
  in the dependency file. No dependency changes were made.
- **Payment workflow is incomplete:** `Payment` and admin configuration exist,
  and orders calculate paid/outstanding/status values from related records.
  There are no payment create/edit/delete forms, views, or routes. The
  `Payment.payment_due` property is an unimplemented stub; the usable
  outstanding balance is calculated on `Order`.
- **Payment validation is unfinished:** there is no implemented rule preventing
  total payments from exceeding an order total. A future payment workflow
  should define overpayment, dates, and correction behavior before exposing
  entry screens.
- **Inventory is not enforced:** new order items link to a harvest, but the app
  does not calculate available quantity or prevent sales exceeding the
  harvested quantity. Order status also does not currently drive stock
  deduction or fulfillment.
- **Connection-lifetime rationale is unknown:** when `DATABASE_URL` is set,
  settings use `conn_max_age=0` and require SSL. The deployment checklist names
  Vercel but does not explain the connection-lifetime choice, and the inspected
  code/history did not establish a rationale. Keep this as an open deployment
  question rather than assuming why it was selected.
- **SQLite file versus configured engine:** a tracked `db.sqlite3` file exists,
  while current settings configure PostgreSQL. The file was not opened or
  inspected, as instructed; its contents and whether it is still needed remain
  unknown.
- **Development testing endpoints:** `/testing/` is routed and requires sign
  in, but `apps/testing/views.py` contains a debug `print`, an unused
  `multiprocessing.context` import, and a hard-coded demonstration name. Its
  name-form handler returns a relative redirect string from
  `/testing/your-name/`; verify the resulting destination against the
  `/<str:name>/` route before relying on that demo. Confirm whether this app
  should remain available in a deployment. This documentation task did not
  alter it.
- **Legacy order-item validation:** `OrderItem.harvest` is optional for historic
  crop-only items, while the new-item form requires a harvest. Model
  `clean()` checks crop/harvest consistency, but direct `.save()` does not call
  `full_clean()` automatically; callers outside validated forms/admin must
  invoke validation explicitly.

## Verified, not an issue

- `AUTH_PASSWORD_VALIDATORS` is configured with Django's similarity,
  minimum-length, common-password, and numeric-password validators. It is not
  empty.
- `.env` is present locally and ignored by `.gitignore`; it was checked only by
  file metadata and was not opened or copied into documentation.
- The request to add comments to static assets conflicts with the instruction
  not to edit `static/`. Static CSS/JavaScript files were intentionally left
  untouched.
- `README.md` was intentionally left untouched.

## Follow-up questions

1. Why was `conn_max_age=0` selected for the hosted PostgreSQL connection, and
   should that remain the deployment's connection policy?
2. Should the tracked SQLite database file be removed from version control or
   retained for a documented purpose? Decide only after its ownership and
   intended use can be safely established.
3. Should `/testing/` be disabled or moved out of the deployed URL table?
4. When payment pages are added, what should happen when installment totals
   exceed the order total, and how should a payment be corrected or reversed?
5. What are the authoritative stock movement rules for fulfilled, cancelled,
   returned, or partially fulfilled sales?
