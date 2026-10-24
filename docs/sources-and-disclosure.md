# Sources and disclosure

OpenAI Codex assisted with architecture, implementation, original SVG artwork, tests, and documentation. The assignment requests mention of Claude Code: **Claude Code assistance was not observed in this session and is not claimed**. This is not represented as unaided human work. A human owner should review authorization, deployment configuration, dependency updates, costs, and the documented email/concurrency limitations and be prepared to explain them independently.

| Dependency | Purpose | Upstream license |
|---|---|---|
| Python | Runtime | PSF |
| Django | Web framework/auth/ORM/admin | BSD-3-Clause |
| Django REST Framework | REST serialization/views | BSD-3-Clause |
| psycopg / psycopg-binary | PostgreSQL driver | LGPL-3.0 with upstream exceptions; bundled components have their own notices |
| django-environ | Environment parsing | MIT |
| WhiteNoise | Static serving | MIT |
| Gunicorn | Linux WSGI server | MIT |
| Tailwind CSS / CLI | CSS compiler | MIT |
| Playwright | Browser testing | Apache-2.0; browser binaries have separate notices |

Retain upstream license notices when redistributing. Transitive packages and browser components also have licenses; the table is not a legal audit. npm lockfile and Python installed-version snapshot record the resolved environment.

All five SVG covers are original geometric artwork generated locally in `scripts/create_covers.py`; no stock photos, external fonts, image hosting, or third-party image licenses are required. Sample articles are AI-assisted editorial examples, not cited factual research.

Technical references consulted:

- [Django 5.2 release notes](https://docs.djangoproject.com/en/5.2/releases/5.2.18/) for the selected supported patch release.
- [Tailwind CLI installation](https://tailwindcss.com/docs/installation/tailwind-cli) for the v4 compilation workflow.
- [Supabase PostgreSQL connection documentation](https://supabase.com/docs/guides/database/connecting-to-postgres) and [connection guidance](https://supabase.com/kb/troubleshooting/using-sqlalchemy-with-supabase-FUqebT) for direct/session connection choices.
- Vendor cost sources are linked in `cost-and-scaling.md`; scenario budgets are hypothetical rather than vendor quotes.

Verification is recorded in `evidence/` and `final-report.md`. Passing SQLite tests does not establish hosted PostgreSQL connectivity or row-lock behavior. Browser screenshots prove only the exercised local views. No Lucidchart artifact, GitHub repository upload, hosted demo, or Supabase connection is claimed without evidence.
