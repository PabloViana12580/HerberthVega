# AGENTS.md

Rules for anyone (human or AI agent) changing this repository.

## Stack and ownership

- Backend: Python and Django (`config/` is the project package).
- Frontend: Django templates, Bootstrap 5, custom CSS (`static/css/app.css`), and minimal vanilla JavaScript (`static/js/app.js`). No React or separate frontend app.
- Authentication: Django's built-in auth (`auth.User`), sessions, permissions, and password hashing. No third-party auth service.
- Database: PostgreSQL only (local server in development; a hosted one such as Supabase later). Django connects directly with database credentials. No SQLite fallback.
- Apps and what they own:
  - `pages`: the marketing pages (home) and business details shown on every page.
  - `catalog`: the `Service` model and the service pages.
  - Future apps keep one responsibility each, e.g. `booking` (availability, appointments), `orders` (cart, checkout, payments), `accounts` (customer sign-up and profiles).
- Change application schema only through Django models and migrations. Do not create or alter app tables with hand-written SQL or a database dashboard. Migrations may use `RunSQL` for PostgreSQL-specific DDL (e.g. row level security).
- Never drop, truncate, or reset database objects you did not create for the task.
- Every table in the `public` schema must have row level security enabled, so the project can move to a hosted PostgreSQL that exposes the schema over HTTP. The test suite enforces this.

## Frontend

- Always read and follow the installed `frontend-design` skill (`.claude/skills/frontend-design`) before implementing or modifying any frontend UI. If it cannot be read, stop and report it.
- Use the brand tokens in `static/css/app.css` (`--cs-spruce` #1F3B33, `--cs-eucalyptus` #5E8170, `--cs-mist` #E4ECE6, `--cs-soap` #FAFBF8, `--cs-lemon` #F2D35B, `--cs-ink` #17231F); don't hardcode other brand colors.
- Extend `templates/base.html`, reuse `templates/components/`, and use named URLs and `{% static %}`.
- Keep pages responsive, keyboard accessible, and readable at AA contrast. Respect `prefers-reduced-motion`.
- Images must be free to use (e.g. Unsplash License) or owned by the business; record each one in `static/img/CREDITS.md`.

## Secrets

- Keep all credentials in environment variables (`.env` locally, which is git-ignored). Update `.env.example` with placeholders when adding a variable.
- Never commit credentials, connection strings, or keys, including in docs, tests, or fixtures.
- Never expose database credentials, payment keys, or other server-side keys to frontend code.

## Commerce and booking behaviour

- Never show a feature as working before it works: no fake booking buttons, no simulated payments, no placeholder prices presented as real.
- Prices, availability, and totals are calculated and validated on the server, never trusted from the browser.
- Bookings must not double-book a time slot; enforce it with database constraints, not only in Python.
- Store money as `DecimalField`, never float. Store times as timezone-aware datetimes (`USE_TZ = True`).

## Working practices

- Implement only the explicitly requested scope; keep code modular and avoid unrelated refactoring.
- Test meaningful behavior with each change (`python manage.py test`). Database tests need PostgreSQL.
- Report actual verification results. Do not claim a check passed unless it ran and passed.
