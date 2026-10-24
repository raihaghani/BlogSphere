# REST API specification

Base path `/api/`. JSON and DRF browsable API are supported. Authentication is Django session cookies, not JWT or Basic Auth. Public GETs exclude drafts even when the caller owns them. Write querysets include authorized owned drafts. Missing and hidden resources return 404. Anonymous or insufficiently privileged unsafe requests return 403 under SessionAuthentication. Validation failures return 400 field-to-message arrays. Unsupported methods return 405.

| Method | Path | Permission | Success |
|---|---|---|---|
| GET | /api/posts/ | Public, published only | 200 paginated posts |
| GET | /api/posts/{id}/ | Public, published only | 200 post |
| POST | /api/posts/ | Author or staff with add_post | 201 post |
| PATCH | /api/posts/{id}/ | Author owner with change_post or staff with change_post | 200 post |
| DELETE | /api/posts/{id}/ | Author owner with delete_post or staff with delete_post | 204, empty |
| POST | /api/posts/{id}/publish/ | Same as PATCH | 200 published post |
| POST | /api/posts/{id}/unpublish/ | Same as PATCH | 200 draft post |
| GET | /api/categories/ | Public | 200 paginated categories |
| POST | /api/categories/ | Staff with add_category | 201 category |
| GET | /api/posts/{id}/comments/ | Public, published parent | 200 paginated comments |
| POST | /api/posts/{id}/comments/ | Authenticated, published parent | 201 comment |

Superusers satisfy Django permissions. Plain staff accounts do not. No category update/delete REST endpoint exists; use Admin. No PUT, API registration, token issuance, or draft-reading API is provided. Authors read/edit drafts in their HTML dashboard; PATCH responses include authorized draft content.

## Bodies and responses

Create post (required title, content, category):
```json
{"title":"A practical Django guide","content":"Plain text article content.","excerpt":"A brief introduction.","category":1,"status":"DRAFT","cover_image":"images/programming.svg"}
```
Status defaults to DRAFT. Title max 200, excerpt max 300; content/title cannot be whitespace. Category must exist. Cover is empty or one of technology/programming/artificial-intelligence/cybersecurity/business under `images/*.svg`. PATCH accepts any subset of writable fields and validates supplied values. Status can also change through PATCH; model save applies the same timestamp policy. `author`, `slug`, timestamps, and IDs are read-only/ignored on input.

Post response includes id, title, slug, content, excerpt, status, author username, category ID, category_detail `{id,name,slug}`, cover_image, created_at, updated_at, and published_at (ISO 8601 or null).

Category input/output: `{"id":1,"name":"Technology","slug":"technology"}`; id is read-only, name max 100 unique, slug max 120 unique URL-safe. Duplicate category values return 400.

Comment input: `{"content":"A thoughtful response."}`. Content is trimmed, required, maximum 2,000 characters. Response: `{"id":1,"post":1,"user":"reader","content":"A thoughtful response.","created_at":"2026-10-24T12:00:00Z"}` (illustrative timestamp). User/post are assigned by server. Comments on draft or absent parents return 404. Comment creation and unpublication coordinate using a row lock on PostgreSQL.

Lists return `{"count":12,"next":"...page=2","previous":null,"results":[...]}` with page size 9. Post ordering is newest publication, then creation, then ID. Comments are oldest first. Categories are alphabetical. Invalid/out-of-range API page returns 404. Search `?search=python` is case-insensitive title/content/excerpt matching. Filter `?category=technology` uses exact category slug. Combine both; unknown category gives an empty list. Search text is capped at 200 characters.

## Session and CSRF: browser, Postman, cURL

1. GET `/login/` to obtain a `csrftoken` cookie.
2. POST form-encoded `username`, `password`, and `csrfmiddlewaretoken` to `/login/`, preserving cookies and same-origin Referer. Django rotates the CSRF token on successful login.
3. Read the new `csrftoken` cookie from the cookie jar. Send it as `X-CSRFToken` on unsafe API requests along with `sessionid` and cookies. For HTTPS, supply the same-origin Referer/Origin.
4. In Postman enable cookie persistence and set `X-CSRFToken` to the current cookie value. Use raw JSON and `Content-Type: application/json`. Do not disable CSRF. POST `/logout/` with the token to end the session.

```bash
curl http://127.0.0.1:8000/api/posts/?search=python
curl -b cookies.txt -H 'X-CSRFToken: CURRENT_TOKEN' -H 'Content-Type: application/json' \
  -H 'Referer: http://127.0.0.1:8000/' \
  -d '{"title":"A new idea","content":"A complete paragraph.","category":1}' \
  http://127.0.0.1:8000/api/posts/
```

`cookies.txt` must come from a real login as described above; the example token is a placeholder. Keep cookie jars outside source control. API writes without a session fail permission checks; authenticated writes without CSRF fail 403. No 409 behavior is invented. Repeated publish is idempotent in resource count/timestamp; repeated POST create is not deduplicated and creates a new story. DELETE after DELETE returns 404.
