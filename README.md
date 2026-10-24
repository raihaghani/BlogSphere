# BlogSphere

A complete Django editorial MVP for FalconXoft Weekend Software Engineering Assignment, Project 01. Readers discover and discuss articles; authors turn drafts into published stories; administrators manage content and accounts.

## Features and roles

Public visitors can browse, search title/content/excerpt, filter by category, and read published stories and comments. Registered Readers can comment. Authors can create, edit, publish, unpublish, and delete their own stories through HTML or session-authenticated REST APIs. Administrators use Django Admin and explicit model permissions. Staff status alone grants no unrestricted content access.

Includes responsive editorial pages, five original local SVG covers, validation feedback, confirmation before deletion, pagination, demo content, and automated authorization tests. No uploads, JWT, social login, or Supabase Auth.

## Stack and architecture

Python 3.12, Django 5.2 LTS, Django REST Framework, Django Templates, Tailwind CSS 4, vanilla JavaScript, PostgreSQL via psycopg, django-environ, WhiteNoise, and Gunicorn on Linux. Versions are pinned in `requirements.txt`; development browser tooling is in `requirements-dev.txt`. npm is used only for CSS compilation.

One Django application serves both HTML and REST. Both use the same Category, Post, Comment, and built-in User models. Category deletion is protected while posts reference it. Post deletion cascades comments. Publication timestamps survive unpublishing. See [architecture](docs/architecture.md) and [database design](docs/database-design.md).

```text
manage.py              Django commands
config/                settings, URL routing, WSGI/ASGI
accounts/              registration and native authentication
blog/                  models, forms, services, pages, admin, commands, tests
api/                   serializers, viewsets, permissions
templates/             shared components and responsive pages
static/                compiled CSS, JavaScript, local SVG images
scripts/               artwork and evaluation artifact tooling
docs/                  engineering and evaluation deliverables
evidence/              actual verification logs and screenshots
```

## Installation

Run every command from this existing project root. Install Python 3.12 and Node.js first.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
npm.cmd ci
npm.cmd run build:css
Copy-Item .env.example .env
```

On macOS/Linux use `python3.12`, `.venv/bin/python`, and `npm` instead. Activate the environment if you prefer the shorter `python` command. Gunicorn runs on Linux, not native Windows.

Set a unique random `SECRET_KEY` in `.env`. Generate one with:

```powershell
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(50))"
```

The implementation session created an ignored local `.env`, an isolated virtual environment, and temporary demo SQLite data. The current `.env` selects Supabase PostgreSQL; the SQLite demo file is inactive. Do not copy development settings into production. Environment variables override `.env`; explicitly set `$env:DEBUG='True'` for local development if your shell already defines `DEBUG=False`.

### Supabase PostgreSQL

Create a Supabase project, then open **Connect** and copy a PostgreSQL connection string. Prefer the direct connection when IPv6 is available, otherwise use the compatible **session pooler**, normally port 5432. Substitute the database password, URL-encoding reserved characters. Do not use the Supabase API key or Auth service. Put the result in ignored `.env` as `DATABASE_URL=postgresql://...`. Set `USE_SQLITE=False`. SSL is required in settings. Source: [Supabase connection guide](https://supabase.com/docs/guides/database/connecting-to-postgres).

Use a separate development/test database or project. Django tests create and destroy a test database; the connection user needs the relevant privilege. Do not point tests or demo seeding at production. Supabase SSL connectivity, migrations, roles, and a rolled-back ORM relationship/publication smoke test were verified on 25 October 2026. The full suite still needs a dedicated PostgreSQL test database; concurrent locking behavior has not been stress-tested.

For an explicit temporary local fallback only, set `USE_SQLITE=True` and `DEBUG=True`. SQLite is refused when DEBUG is false. This does not demonstrate PostgreSQL compatibility testing.

### Initialize and run

```powershell
$env:DEBUG='True'
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py setup_roles
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py seed_demo
.\.venv\Scripts\python.exe manage.py runserver
```

Visit `http://127.0.0.1:8000/`. `seed_demo` is optional, repeatable, and refuses DEBUG=False. Its editorial user has an unusable password. Create your own account and promote it in Admin â†’ Users â†’ Groups â†’ Author. Do not mark ordinary authors as staff. Run `setup_roles` after migrations; rerunning safely reconciles Author permissions.

An administrator is normally a superuser created interactively. A limited staff account needs explicit appropriate model permissions. Granting user/group management permissions is privileged: such administrators can change access assignments and should be trusted accordingly.

For CSS development: `npm.cmd run watch:css`. Compiled CSS is committed so deployment can collect it without a runtime Node dependency.

## API

`GET /api/posts/` and `/api/posts/<id>/` expose published stories only, including to owners. Search with `?search=python`, filter with `?category=technology`, paginate with `?page=2`. Authors can POST drafts, PATCH/DELETE owned posts, and POST `publish/` or `unpublish/`. Comments use `/api/posts/<id>/comments/`; categories use `/api/categories/`. See [full API specification](docs/api-spec.md) for bodies, responses, CSRF, and Postman steps.

## Verification

```powershell
$env:DEBUG='True'
$env:USE_SQLITE='True' # Explicit isolated local fallback; omit only for a dedicated PostgreSQL test database.
.\.venv\Scripts\python.exe manage.py test blog.tests.test_platform --verbosity 2
.\.venv\Scripts\python.exe -m playwright install chromium
.\.venv\Scripts\python.exe manage.py test blog.tests.test_browser --verbosity 2
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py collectstatic --noinput
```

The full suite includes browser tests and requires installed Chromium. Test databases are isolated by Django. Browser screenshots contain disposable test content. Consult `evidence/` and `docs/final-report.md` for executed results, not just available test code.

After fallback testing, remove the shell override with `Remove-Item Env:USE_SQLITE` to resume the database selected in `.env`. To verify the configured Supabase connection and apply migrations without printing credentials, run `.\.venv\Scripts\python.exe scripts\connect_supabase.py`. The helper requires SSL and reports sanitized failures.

## Production deployment

Deploy to Linux with Python 3.12. Install `requirements.txt`, build CSS in CI (or use the committed build), and supply a real secret, PostgreSQL URL, explicit `ALLOWED_HOSTS`, and HTTPS origins in `CSRF_TRUSTED_ORIGINS`. Set `DEBUG=False`, `USE_SQLITE=False`, and all three `DJANGO_*SECURE*` settings to True. Secure defaults apply when omitted. Never copy the development False settings blindly.

```bash
python manage.py migrate
python manage.py setup_roles
python manage.py collectstatic --noinput
python manage.py check --deploy
gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 2 --access-logfile - --error-logfile -
```

Put Gunicorn behind an HTTPS reverse proxy and supervise it with systemd or your platform. If TLS terminates at a proxy, configure `SECURE_PROXY_SSL_HEADER` only after establishing that the proxy strips client-provided forwarded headers and supplies its own trusted value; otherwise use TLS through to the application. Configure health monitoring, log retention, database backups, and tested restores. Review HSTS subdomain coverage before enabling it on an existing domain. WhiteNoise serves versioned static files. No uploaded media storage is required.

Deploy checks against development settings intentionally warn about DEBUG, cookies, and HTTPS; production checks must use production configuration. No deployment or GitHub push was performed.

## Security and limitations

Native password hashing/validators, session authentication, POST-only logout, CSRF, escaped plain-text content, ORM queries, server-side ownership checks, restricted static image choices, and production security headers are enabled. UUID-suffixed slugs remain stable; uniqueness is database-enforced. API author/user fields are read-only.

Email registration rejects case-insensitive duplicates and normalizes to lowercase. The built-in User table has no database uniqueness constraint on email: concurrent registrations and out-of-band admin writes can still create duplicates. This is an explicitly documented MVP limitation, not a guarantee of global uniqueness. No email verification, password reset delivery, login throttling, or rich-text editor is implemented. Add rate limiting at the deployment proxy before public exposure. Database model validation is used for normal saves; direct SQL/bulk updates bypass Python validation and must be controlled.

Potential next steps: database-enforced normalized email uniqueness through a reviewed migration, verified email/password reset delivery, PostgreSQL full-text search after measurement, and audit logging. A dedicated PostgreSQL test-suite run, Lucidchart recreation/export, GitHub publishing, and hosting remain manual actions.

## Engineering artifacts and disclosure

See `docs/` for architecture, ERD, API workflows, decision trade-offs, cost/scaling scenarios, test workbook, and sources. AI assistance was provided by OpenAI Codex; no Claude Code execution was observed or claimed. Human review and independent explanation remain necessary. Original SVG illustrations have no external image dependencies.

Repository: **not yet published**. Live demo: **not yet deployed**.
