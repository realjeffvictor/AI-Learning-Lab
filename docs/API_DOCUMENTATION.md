# API Conventions (planning; endpoints documented per phase)

- Base path: /api/v1. JSON only. Resource-oriented plural nouns. Auto OpenAPI at /docs (disabled or protected in production).
- Auth: short-lived access JWT (about 15 min) in Authorization: Bearer; rotating refresh token in an HttpOnly, Secure,
  SameSite cookie, stored hashed server-side for revocation. CSRF protection on cookie-authenticated refresh/logout.
- Status codes: 200, 201, 204, 400, 401, 403, 404, 409, 422, 429, 500.
- Error envelope: {"error": {"code": "string_code", "message": "human text", "details": [...], "request_id": "..."}}
- Pagination: ?page=1&page_size=20 → {"items": [...], "page": 1, "page_size": 20, "total": 0}
- Filtering/sorting: explicit whitelisted query params only.
- Naming: snake_case JSON. ISO 8601 UTC timestamps.
- Versioning: breaking changes go to /api/v2.
- Authorization: role guards as dependencies plus ownership checks in services. Frontend checks are cosmetic only.
- Rate limits: strict on auth and AI endpoints; per-user daily AI quotas via ai_usage_counters.

## Planned endpoint groups
health; auth (register, login, refresh, logout); users/me; courses, modules, lessons; progress; exercises and submissions
(with immediate score + concept results); recommendations; projects and project-submissions; ai (tutor, code, debug,
architecture, testing, docs, review); competencies; achievements and certificates; notifications; admin and instructor
(content CRUD, enrollments, analytics, users).

## Implemented endpoints

### Phase 1
GET /api/v1/health: 200 {"status": "ok", "service": str, "version": str, "environment": str, "timestamp": ISO 8601 UTC}
Every response carries X-Request-ID. Errors use the envelope above.

### Phase 2
Auth model: access JWT in Authorization: Bearer (15 min, no role claim); refresh token in HttpOnly cookie ail_refresh (path /api/v1/auth).
POST /auth/refresh and /auth/logout also require header X-CSRF-Protection: 1.

POST /auth/register {email, password (10 to 128 chars), display_name} -> 201 {access_token, token_type, expires_in, user}; 409 email_taken
POST /auth/login {email, password} -> 200 same body; 401 invalid_credentials; 403 account_disabled; 429 too_many_attempts (+ Retry-After)
POST /auth/refresh -> 200 same body (rotates the cookie); 401 invalid_refresh_token; 403 csrf_failed
POST /auth/logout -> 204 (revokes the token family, clears the cookie)
GET /users/me -> 200 user
PATCH /users/me/profile {display_name?, bio?, experience_level?} -> 200 user
GET /users?page=&page_size= (admin) -> 200 {items, page, page_size, total}
PATCH /users/{id} {role?, is_active?} (admin) -> 200 user; 400 cannot_modify_self; 404 user_not_found
GET /health now also returns "database": ok | unavailable | not_configured.
