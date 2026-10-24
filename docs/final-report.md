# BLOGSPHERE DEVELOPMENT REPORT

Verification date: 25 October 2026, Asia/Karachi.

## 1. IMPLEMENTED FEATURES

Registration, session login and POST logout, published article browsing, search, categories, comments, author dashboard, draft creation/editing, publish/unpublish, confirmed deletion, and Django Admin content management. Required application modules, templates, assets, migrations, dependencies, and engineering documents are present. Tests are consolidated under `blog/tests/` rather than duplicated across apps.

## 2. TECHNOLOGY STACK

Python 3.12; Django 5.2.18 LTS; DRF 3.16.1; psycopg 3.2.10; PostgreSQL on Supabase; Django Templates; Tailwind 4.1.13; vanilla JavaScript; WhiteNoise; django-environ. Gunicorn is configured for Linux and has not been executed on this Windows host. `pip check` found no broken requirements; npm confirmed the required compiler dependencies are installed.

## 3. DATABASE STATUS

Verified a real Supabase connection through DATABASE_URL using psycopg with SSL in use and a successful SELECT 1. Migration generation found no model changes; all migrations are applied, with no pending migrations. Reader and Author groups were initialized idempotently. The active application uses PostgreSQL, not the retained SQLite demo file.

A PostgreSQL transaction verified related User/Category/Post/Comment writes, publication retries and timestamp preservation, draft filtering, protected category deletion, and cascading comment deletion. The transaction rolled back all temporary content and accounts. No demo content was seeded into Supabase during this verification.

## 4. AUTHENTICATION STATUS

Registration validation, password hashing, login, safe redirect handling, and POST-only logout passed automated checks. The Chromium journey exercised registration/login/logout. Credentials were not printed during this verification run. Environment files are ignored by Git. An earlier malformed-line disclosure was reported to the user, who subsequently reported rotating the password; raw parser logging is now suppressed.

## 5. ROLE/PERMISSION STATUS

Backend tests cover Reader denials, Author ownership, forged identity input, private dashboards, and limited staff permissions. Reader and Author groups exist in Supabase. Administrative user creation remains an interactive owner action if no administrator exists yet.

## 6. REST API STATUS

Implemented published post list/detail, author creation, owner/admin PATCH and DELETE, publish/unpublish actions, category list/admin creation, and published-parent comment list/creation. Authorization, validation, draft privacy, pagination/filtering/search, and session CSRF behavior passed tests. Live local post/category list endpoints returned HTTP 200 using Supabase.

## 7. FRONTEND STATUS

Tailwind compilation and WhiteNoise static collection succeeded. Browser tests cover the publishing journey, mobile dashboard/editor overflow, and 390/768/1440-pixel views. The live homepage, login, registration, and compiled stylesheet returned HTTP 200. Screenshots are retained in `evidence/`. These checks do not constitute exhaustive cross-browser or accessibility certification.

## 8. TEST RESULTS

- 39 automated tests passed: 38 backend tests and one multi-step Chromium workflow; latest run 11.489 seconds.
- The automated suite used Django's isolated SQLite test database, explicitly enabled only for that process.
- Real PostgreSQL transactional ORM smoke checks passed separately.
- Django system checks: no issues. Migration drift: no changes detected.
- Python dependencies: no broken requirements. Tailwind build and collectstatic: passed.
- Previous production-style security checks passed using supplied production environment flags; this development server intentionally uses local HTTP settings.
- Full automated execution against an isolated PostgreSQL test database, concurrent locking stress, and production load tests have not been performed.

Evidence: `evidence/verification-tests.txt`, `evidence/test-results.json`, `evidence/current-verification.md`, and browser screenshots. Older logs may describe intermediate failures; the latest verification log is authoritative for this run.

## 9. DOCUMENTATION CREATED

README; architecture and ERD Mermaid sources; endpoint specification; success/failure API sequence diagrams; engineering decisions; cost/scaling analysis; sources/AI disclosure; test-case and cost/scaling XLSX workbooks; this report. Cost figures are explicitly illustrative estimates. Workbooks were rendered and inspected; cost formulas and representative input sensitivity were checked during creation.

## 10. EXTERNAL INTEGRATIONS REQUIRED

Supabase is verified. GitHub publishing, hosted deployment, and Lucidchart recreation/export have not been performed. Mermaid diagram sources are available for that work.

## 11. KNOWN LIMITATIONS

Email uniqueness is application-validated and does not prevent concurrent or admin-created duplicate emails at database level. No email verification, password-reset delivery, login rate limiting, or edit conflict versioning is implemented. Gunicorn and production proxy configuration require Linux verification. The full PostgreSQL test suite still needs a dedicated test database.

## 12. COMMANDS TO RUN LOCALLY

The development server was started at **http://127.0.0.1:8000/** with Supabase enabled. It runs as background process 22932 for this verification session. To restart from the project root:

```powershell
$env:DEBUG='True'
$env:USE_SQLITE='False'
$env:DJANGO_SECURE_SSL_REDIRECT='False'
$env:DJANGO_SESSION_COOKIE_SECURE='False'
$env:DJANGO_CSRF_COOKIE_SECURE='False'
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

For isolated local tests, set `$env:USE_SQLITE='True'` in the test shell, run `.\.venv\Scripts\python.exe manage.py test`, then remove that override with `Remove-Item Env:USE_SQLITE`. Do not direct the full test suite at a shared production database.

## 13. REMAINING MANUAL ACTIONS

Create an administrator interactively if needed (`manage.py createsuperuser`), then assign Author groups through Admin. Optionally seed demo content only into an intended development database. Arrange a dedicated PostgreSQL test environment, production hosting/security configuration, GitHub publication, and Lucidchart exports. No public deployment is claimed.
