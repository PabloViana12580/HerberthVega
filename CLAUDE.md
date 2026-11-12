# CLAUDE.md

A website and, in time, an online store for a home cleaning business: customers browse services, choose a date and time, and book (and later pay). Django + PostgreSQL + Django templates with Bootstrap. The business name and contact details are placeholders (`BUSINESS_*` settings) until the owner confirms them. The layout follows the owner's reference site (renovee.com, a remodeling contractor): header with a services menu, hero, services, why choose us, who we are, contact, footer. `README.md` is for the owner and stays non-technical; technical documentation is in `docs/DEVELOPER.md`.

Project rules (stack, secrets, row level security, frontend skill, commerce rules) are in `AGENTS.md` and apply here:

@AGENTS.md

## Commands

Windows with Git Bash. The virtualenv is `.venv` (Python 3.13); call its interpreter directly, no activation needed.

```bash
.venv/Scripts/python.exe manage.py runserver                 # http://127.0.0.1:8000, needs .env
.venv/Scripts/python.exe manage.py check
.venv/Scripts/python.exe manage.py makemigrations --check --dry-run
.venv/Scripts/python.exe manage.py migrate
.venv/Scripts/python.exe manage.py test --noinput
.venv/Scripts/python.exe manage.py createsuperuser           # owner account for /admin/
```

Configuration comes from `.env` at the repo root (git-ignored, loaded by `config/settings.py` with python-dotenv). `.env.example` lists every variable. Locally you need `DATABASE_URL` and `DJANGO_DEBUG=true` (without debug, `DJANGO_SECRET_KEY` is required).

## Layout

| Path | Responsibility |
| --- | --- |
| `config/` | Settings (`database_from_env()`, business details, security), URLs, `/healthz`, `test_runner.py`, project-level tests (settings, auth, RLS). |
| `pages/` | Home page view and template; `context_processors.business` puts `business.name/phone/phone_href/email/service_area/hours` in every template. |
| `catalog/` | `Service` model, admin, list/detail views, `context_processors.nav_services` (header and footer menu). |
| `templates/` | `base.html`, `components/` (brand, header, footer, service card, price, contact buttons, password field), `registration/login.html`. |
| `static/` | `css/app.css` (brand tokens as `--cs-*`), `js/app.js`, `img/` (Unsplash photos; credits in `img/CREDITS.md`). |

URLs: `/`, `/services/`, `/services/<slug>/`, `/accounts/login/`, `/accounts/logout/` (POST only), `/admin/`, `/healthz`.

## Data model

- `Service` (UUID pk): name and slug (both unique), summary, description, `includes` (one checklist item per line, exposed as `includes_list`), `price_from` (nullable Decimal, check constraint >= 0; empty shows "Price on request"), `duration_minutes`, `image` (static path) and `image_alt`, `is_active`, `sort_order`.
- Migrations: 0001 `Service`, 0002 RLS on Django's tables and `catalog_service`, 0003 five starter services (no prices).
- New table or model: add a migration that enables RLS (copy `catalog/migrations/0002_enable_row_level_security.py`). `test_row_level_security_enabled_on_all_public_tables` in `config/tests.py` fails otherwise.

## Database

- Local PostgreSQL 18 (Windows service `postgresql-x64-18`, port 5432). The app uses its own role `cleaning_app` (with `CREATEDB` for the test database) and database `cleaning_service`; see `docs/DEVELOPER.md` "Create the local database". `sslmode=disable` is accepted only for localhost hosts.
- Tests create and drop `test_cleaning_service` on the same server.

## Conventions and pitfalls

- **New environment variable**: add it to `config/settings.py`, `.env.example`, and the variable table in `docs/DEVELOPER.md`.
- **Booking is not built.** Calls to action point to phone and email (`components/contact_options.html`); replace them when booking exists, never with a non-working button.
- **Copy is a draft.** The home page "Why customers choose us" and "Who we are" text and the starter services are drafts for the owner to confirm.
- **Line endings**: Git on this machine uses `core.autocrlf=true`; files are LF.
- Scripts run outside `manage.py` need `PYTHONPATH` set to the repo root and `DJANGO_SETTINGS_MODULE=config.settings`.
- Not on GitHub yet; nothing is deployed. Settings are already production-ready (WhiteNoise, `/healthz`, HTTPS redirect when `DEBUG` is off, `RENDER_EXTERNAL_HOSTNAME`).

## Next steps

1. Owner confirms business name, phone, email, area, hours, prices, and copy.
2. `booking` app: availability (working hours, blackout days), appointments with a database constraint against overlapping bookings for the same team, booking form on the service page.
3. Customer accounts (`accounts` app) and email confirmations.
4. `orders` app: cart and checkout with a payment provider (e.g. Stripe Checkout), keys server-side only.
5. Hosting (e.g. Render free tier) and a hosted PostgreSQL (e.g. Supabase free tier).
