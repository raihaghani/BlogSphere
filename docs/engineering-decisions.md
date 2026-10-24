# Engineering decisions

| Decision | Selected approach and rationale | Advantages | Trade-offs and limitations |
|---|---|---|---|
| Django vs Express | Django 5.2 LTS provides ORM, forms, authentication and admin in one supported framework | Consistent security defaults and less integration work | More conventions and synchronous request overhead; Express offers a smaller JavaScript core but needs additional choices |
| Templates vs React | Server-rendered Django Templates fit article browsing and form workflows | One deployment, accessible HTML, less client state | Full-page form transitions; React would help a much more interactive editor but adds build/API/state complexity |
| PostgreSQL vs MongoDB | Relational PostgreSQL expresses article/category/user/comment relationships | FK integrity, transactions, indexes, mature operations | Schema migrations need review; MongoDB flexibility does not justify weaker relational modeling here |
| Django ORM vs Prisma | Native ORM uses the same Python model metadata for forms/admin/DRF | Fewer runtimes, coherent migrations and query tools | Complex queries still require SQL understanding; Prisma would add a Node-oriented data layer |
| Sessions vs JWT | Database-backed Django sessions with CSRF | Immediate server-side session logout, native admin integration | Cookie/CSRF handling required; JWT introduces token revocation/storage complexity without a mobile or cross-service requirement |
| Django Admin vs custom admin | Built-in Admin with model permissions | Mature user/group/category/comment management | Less custom UX; staff permission grants require careful administration |
| PostgreSQL search vs Elasticsearch | ORM icontains across title/content/excerpt initially | Simple, portable, no search service | Substring scans can be expensive; evaluate PostgreSQL full-text/GIN indexes before Elasticsearch, which adds cluster/index synchronization burden |
| Monolith vs microservices | One Django backend with three small apps | One transaction boundary, easy local operation | Application scales as a unit; independent services would add distributed failures and authorization duplication |

## Additional choices

- Local SVG covers avoid uploads, remote assets, and image processing risk.
- UUID suffixes avoid title-collision query races; slugs remain readable and stable.
- Preserved original publication dates make unpublish/republish predictable.
- Category PROTECT avoids silently deleting or orphaning articles.
- Public APIs never expose drafts, even to owners. Dashboard HTML handles private reading; write responses return owned draft state.
- Reversible local tests explicitly enable SQLite. PostgreSQL remains required for deployment; locking and connection behavior need hosted verification.
- Email uniqueness is application-validated because the mandated built-in User model does not provide it. Documented race/admin limitations remain; a database index migration requires a deliberate policy for empty emails and existing records.
- Versioned dependencies and committed CSS make builds repeatable. Python transitive versions are recorded separately from the portable direct dependency file.
- Browser tests use a Django-managed isolated live test database, disposable accounts, and random credentials.

## Deviations and incomplete external deliverables

Supabase credentials were supplied locally during implementation. SSL connectivity, migrations, roles, and a transactional ORM smoke test are verified. GitHub upload, deployment, and Lucidchart export remain unperformed; editable diagram sources are included. Codex performed this implementation. Claude Code was named in the assignment, but no Claude Code assistance was observed and it would be inaccurate to attribute work to it.
