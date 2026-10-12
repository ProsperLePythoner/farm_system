# Agribusiness Management System — Vercel Deployment Checklist

**Project:** `farm_system`  
**Repository:** `https://github.com/ProsperLePythoner/farm_system`  
**Deployment target:** Vercel + managed PostgreSQL  
**Status:** Planning / Phase 1 not yet verified  
**Last updated:** 12 October 2026

---

## Purpose

Deploy the Django Agribusiness Management System safely, while preserving the existing local development setup.

We will work through the phases in order. Complete and verify each checkpoint before proceeding to the next. Do not mark a task complete merely because a command ran; confirm the expected result.

## Ground rules

- [ ] Keep local development working throughout deployment.
- [ ] Keep `.env`, database passwords, Django secret keys, and other credentials out of GitHub.
- [ ] Use GitHub Desktop for repository commits and pushes.
- [ ] Use separate configuration and credentials for local development and production.
- [ ] Use a managed, remotely accessible PostgreSQL database for production. Vercel cannot connect to PostgreSQL running only on a home PC.
- [ ] Never paste secrets into chat, commit messages, source code, screenshots, or public issue reports.
- [ ] Test production-critical changes before relying on them with real farm records.
- [ ] Record any decisions or problems in the notes section at the end.

## Phase 1 — Secure and prepare the repository

**Goal:** Ensure the repository is safe and contains the code needed for deployment.

- [ ] Open `farm_system` in GitHub Desktop.
- [ ] Review the **Changes** tab.
- [ ] Confirm `.env` is **not** listed as a change.
- [ ] Confirm `.gitignore` excludes `.env`, `.env.*`, virtual environments, local database files, and generated files as appropriate.
- [ ] Review `config/settings.py` and confirm secrets are read from environment variables rather than hardcoded.
- [ ] Remove any old credentials from source code, comments, and tracked files.
- [ ] Confirm `requirements.txt` includes the dependencies required to run the project.
- [ ] Confirm essential Django files and app folders are present.
- [ ] Commit reviewed changes in GitHub Desktop with a clear message.
- [ ] Click **Push origin** in GitHub Desktop.
- [ ] Check the GitHub repository in the browser to confirm the commit arrived and `.env` is absent.

**Checkpoint:** The latest safe code is on GitHub, and no secret file or credential is tracked.

> If `.env` appears in GitHub Desktop's Changes tab, stop. Do not commit or push it. If a secret was ever pushed to a public repository, treat it as compromised and rotate it; deleting it from the latest commit alone does not undo exposure.

## Phase 2 — Prepare Django for production

**Goal:** Make the project behave securely and reliably outside local development.

- [ ] Confirm local development still starts and connects to the local PostgreSQL database.
- [ ] Configure `DEBUG` from an environment variable, defaulting to `False` when not explicitly set.
- [ ] Configure `ALLOWED_HOSTS` from an environment variable; do not use a permissive wildcard in production.
- [ ] Configure `CSRF_TRUSTED_ORIGINS` for the actual HTTPS production domain.
- [ ] Review Django's `SECRET_KEY` handling and ensure production uses a strong, private value distinct from any exposed key.
- [ ] Review secure-cookie and HTTPS-related settings for the hosting environment.
- [ ] Verify static-file configuration, including `STATIC_ROOT` and the hosting approach for collected static assets.
- [ ] Check template paths, URL configuration, WSGI entry point, and installed applications.
- [ ] Check the production dependency list and supported Python/Django versions.
- [ ] Review file uploads and media storage, if the application uses them.
- [ ] Run Django's deployment checks and address applicable warnings.

**Checkpoint:** The project has a documented, tested production configuration while local development still works.

## Phase 3 — Create the production PostgreSQL database

**Goal:** Provision a database reachable securely by the deployed application.

- [ ] Compare suitable managed PostgreSQL providers and select one compatible with the application and deployment region.
- [ ] Create a production database and a dedicated database user where supported.
- [ ] Save the connection details in a private password manager or other secure location.
- [ ] Confirm TLS/SSL requirements and configure the Django database connection accordingly.
- [ ] Check connection/network restrictions required by the provider.
- [ ] Keep the production database separate from the local development database.
- [ ] Plan how database backups and restoration will work.
- [ ] Do not copy real production records into test environments without an approved need and appropriate safeguards.

**Checkpoint:** A secure production database exists, and its connection requirements are understood. Do not put its credentials in the repository.

## Phase 4 — Connect GitHub to Vercel

**Goal:** Link the repository to Vercel and establish deployment configuration.

- [ ] Sign in to Vercel.
- [ ] Connect the correct GitHub account and grant access to `ProsperLePythoner/farm_system`.
- [ ] Import the repository as a Vercel project.
- [ ] Confirm the project root directory and the repository's Django/Python layout.
- [ ] Verify the current Vercel-supported Python/Django deployment method before adding configuration files.
- [ ] Configure build/runtime settings based on that verified method.
- [ ] Add production environment variables in Vercel's project settings.
- [ ] Use production database values and a separate production Django secret key.
- [ ] Set production `DEBUG` to `False`.
- [ ] Set `ALLOWED_HOSTS` and CSRF trusted origins to the actual deployed hostname(s).
- [ ] Ensure secrets are set for the intended Vercel environments, especially Production.
- [ ] Confirm Git integration and the intended production branch (normally `main`).

**Checkpoint:** Vercel is connected to the correct repository, and production environment variables are configured privately.

## Phase 5 — Perform the first deployment

**Goal:** Get a first deployment running and initialise the database safely.

- [ ] Trigger the initial deployment.
- [ ] Inspect build logs and resolve dependency, configuration, or runtime errors.
- [ ] Confirm the deployment starts successfully and identify its assigned URL.
- [ ] Verify that the hostname matches the configured `ALLOWED_HOSTS` and CSRF settings.
- [ ] Apply Django migrations to the **production** database using a deliberate, verified process.
- [ ] Create the initial Django administrator account securely.
- [ ] Confirm static assets, CSS, images, and templates load correctly.
- [ ] Check application logs for startup errors or database connection failures.
- [ ] Confirm the app does not rely on writing persistent data to an ephemeral deployment filesystem.

**Checkpoint:** The site loads on its production URL and can read/write the production database.

> Database migrations change the production schema. Review them before applying them, and establish a backup/rollback plan appropriate to the change. Do not assume a serverless build automatically runs migrations safely.

## Phase 6 — Verify live application functionality

**Goal:** Confirm the live site works correctly and respects permissions.

- [ ] Open the production URL over HTTPS.
- [ ] Test login and logout.
- [ ] Test that anonymous users cannot access protected pages.
- [ ] Test each user role and verify that users cannot perform actions outside their permissions.
- [ ] Test dashboard content and navigation.
- [ ] Test fields, crops, and planting records.
- [ ] Test harvest recording and upcoming harvest information.
- [ ] Test customer records.
- [ ] Test orders, order items, payments, totals, and outstanding balances.
- [ ] Verify invalid form submissions display useful errors.
- [ ] Check page layout and usability on desktop and mobile widths.
- [ ] Confirm that no secret values appear in pages, logs, or error messages.
- [ ] Confirm that test records created during verification are clearly identified and cleaned up when appropriate.

**Checkpoint:** The core workflows pass a documented smoke test, and role permissions behave as intended.

## Phase 7 — Establish a safe release workflow

**Goal:** Make future updates predictable and reversible.

- [ ] Make and test changes locally first.
- [ ] Review changes in GitHub Desktop before committing.
- [ ] Push reviewed commits to GitHub.
- [ ] Use Vercel preview deployments for changes when practical.
- [ ] Verify the preview before merging changes into the production branch.
- [ ] Review model changes and generated migrations before deployment.
- [ ] Apply production migrations using the established migration procedure.
- [ ] Verify the production deployment after each release.
- [ ] Monitor deployment/runtime logs when something fails.
- [ ] Keep secrets, dependency versions, and production settings maintained.
- [ ] Schedule and periodically test database backups and restoration.

**Checkpoint:** There is a repeatable path from local development to preview testing to production.

---

## Progress tracker

Use this table to record the current state. Update it as each phase is verified.

| Phase | Status | Notes |
|---|---|---|
| 1. Repository security and preparation | Not verified | Check GitHub Desktop; ensure `.env` is absent |
| 2. Django production readiness | Not started | Verify current Vercel Django/Python deployment method |
| 3. Production PostgreSQL | Not started | Choose provider and configure secure connectivity |
| 4. GitHub–Vercel integration | Not started | Import repository and set environment variables |
| 5. First deployment | Not started | Inspect logs and initialise production database |
| 6. Live smoke tests | Not started | Test workflows and permissions |
| 7. Release workflow | Not started | Establish preview and production release process |

**Status key:** `Not started` · `In progress` · `Blocked` · `Verified`

## Current next action

Start with **Phase 1**:

1. Open GitHub Desktop and select `farm_system`.
2. Inspect the **Changes** tab.
3. Confirm `.env` is not listed.
4. Review the pending changes before committing or pushing.
5. If uncertain, stop and inspect the file list before proceeding.

We can complete the phases together one checkpoint at a time. This document is a working checklist, not a claim that the deployment has already been completed.

## Decisions and notes

- **Production database provider:** TBD
- **Vercel project name:** TBD
- **Production domain:** TBD
- **Production branch:** `main` (confirm during setup)
- **Verified Django/Vercel deployment approach:** TBD
- **Migration procedure:** TBD
- **Backup/restore procedure:** TBD
- **Outstanding blockers:** None recorded yet
