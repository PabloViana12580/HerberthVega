# Developer guide

## Architecture

Django 5.2 project (`config/`) with two apps:

- `pages`: home page; `context_processors.business` exposes the business details from settings to every template.
- `catalog`: the `Service` model, admin, and service list and detail pages; `context_processors.nav_services` feeds the header and footer menus.

Templates are server-rendered (`templates/base.html` plus `templates/components/`) with Bootstrap 5.3.3 from jsDelivr (SRI hashes), `static/css/app.css` (brand tokens `--cs-*`), and `static/js/app.js`. Fonts: Bricolage Grotesque and Figtree from Google Fonts. PostgreSQL only; every table has row level security enabled by migration. WhiteNoise serves static files in production.

## Local setup

Requirements: Python 3.13 and PostgreSQL (16 or newer; this machine has 18).

```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
cp .env.example .env        # then fill in the values
```

### Create the local database

The app uses its own role and database instead of the `postgres` superuser. Run once as `postgres` (psql asks for the postgres password), replacing the password with the one in your `.env`:

```sql
-- psql -h localhost -U postgres
CREATE ROLE cleaning_app LOGIN CREATEDB PASSWORD 'the-password-from-.env';
CREATE DATABASE cleaning_service OWNER cleaning_app;
```

`CREATEDB` lets the test runner create and drop `test_cleaning_service`. Then:

```bash
.venv/Scripts/python.exe manage.py migrate
.venv/Scripts/python.exe manage.py createsuperuser
.venv/Scripts/python.exe manage.py runserver
```

Open http://127.0.0.1:8000/ for the site and http://127.0.0.1:8000/admin/ to manage services.

## Environment variables

| Variable | Required | Purpose |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | Yes unless `DJANGO_DEBUG=true` | Django signing key. |
| `DJANGO_DEBUG` | No | `true` for local development only. Off means secure cookies and HTTPS redirect. |
| `DJANGO_ALLOWED_HOSTS` | No | Comma-separated host names (default `localhost,127.0.0.1`). |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | No | Comma-separated `https://` origins for a custom domain. |
| `DJANGO_SECURE_SSL_REDIRECT` | No | Override the HTTPS redirect (default: on when debug is off). |
| `DJANGO_TIME_ZONE` | No | IANA time zone for scheduling (default `America/New_York`). |
| `DATABASE_URL` | Yes (or the `DB_*` variables) | `postgresql://user:password@host:port/db`; add `?sslmode=disable` for a local server without TLS. |
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | Alternative to `DATABASE_URL` | Individual connection settings. |
| `DB_SSLMODE`, `DB_SSLROOTCERT` | No | TLS mode (default `require`; weaker modes only for localhost) and CA file. |
| `DB_CONN_MAX_AGE` | No | Seconds to reuse connections (default 60). |
| `BUSINESS_NAME`, `BUSINESS_PHONE`, `BUSINESS_EMAIL`, `BUSINESS_SERVICE_AREA`, `BUSINESS_HOURS` | No | Business details shown on every page (placeholder defaults). |
| `RENDER_EXTERNAL_HOSTNAME` | Set by Render | Added to allowed hosts and CSRF origins. |

## Tests

```bash
.venv/Scripts/python.exe manage.py test --noinput
```

Covers settings parsing, the health check and production settings, row level security on every public table, sign-in and sign-out, admin access, the `Service` model and its constraints, the service pages, and the home page.

## Managing services

Services are edited in the admin (`/admin/catalog/service/`). `includes` takes one checklist item per line. `image` is a path under `static/`, e.g. `img/deep-clean.jpg`; add new photos to `static/img/` and record them in `static/img/CREDITS.md`. Leave `price_from` empty to show "Price on request".
