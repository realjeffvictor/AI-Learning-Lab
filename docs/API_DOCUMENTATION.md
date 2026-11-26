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

### Phase 3 (all require a Bearer access token)
GET /courses -> [CourseSummary] (counts of published, planned and completed lessons, enrolled flag)
GET /courses/{course_slug} -> CourseDetail (modules, lessons, per-lesson progress); 404 course_not_found
GET /courses/{course_slug}/modules/{module_slug}/lessons/{lesson_slug} -> LessonDetail (content_md is null for planned lessons, previous/next links); 404 lesson_not_found
POST /courses/{course_slug}/enrollment -> 200 {course_slug, enrolled_at} (idempotent)
GET /progress/summary -> {lessons_completed, time_spent_seconds, courses, competencies, up_next}
POST /progress/lessons/{lesson_id}/start -> progress (also enrols); 409 lesson_unavailable for planned lessons
POST /progress/lessons/{lesson_id}/time {seconds 1..120} -> progress; 409 progress_not_started. Credit is capped by elapsed wall-clock time.
POST /progress/lessons/{lesson_id}/complete -> progress (idempotent; concept exposure counted once)

### Phase 4 (all require a Bearer access token)
GET /lessons/{lesson_id}/exercises -> [ExercisePublic] (answers, explanations and puzzle order are never included); 404 lesson_not_found; [] for planned lessons
POST /exercises/{exercise_id}/submissions {answer} -> 201 {score, passed, pass_score, attempt_number, feedback, concept_results, recommendations}; 422 invalid_answer; 404 exercise_not_found
  quiz answer: {"answers": {question_id: option_index}}; puzzle answer: {"order": [item_id, ...]}; code answer: {"code": str, "results": [{"id", "passed"}]} (results are reported by the browser)
GET /exercises/{exercise_id}/submissions -> latest 20 attempts, newest first
GET /assessments/mastery -> per-concept correct and total, using the latest attempt at each exercise

### Phase 5 (all require a Bearer access token)
GET /ai/status -> {enabled, model, usage}
POST /ai/chat {assistant, mode, message (1..4000), conversation_id?, lesson_id?, exercise_id?, code? (max 8000)} -> {conversation_id, assistant, mode, reply, usage}
  assistant: tutor|code|debug|architecture|testing|docs|review. mode: independent|hint|pair|generate|review. The review assistant always runs in review mode.
  Errors: 403 ai_disabled_in_mode, 503 ai_not_configured, 429 ai_daily_limit, 502 ai_provider_error, 404 lesson_not_found|exercise_not_found|conversation_not_found, 409 conversation_mismatch
POST /ai/study-plan -> {reply, weak_concepts, recommendations, usage}; the reply never contains URLs
GET /ai/conversations -> latest 20; GET /ai/conversations/{id} -> messages; DELETE /ai/conversations/{id} -> 204. All filtered by owner.

### Phase 6 (all require a Bearer access token)
GET /projects -> [ProjectSummary] with the caller's status (not_started|draft|submitted|approved|changes_requested)
GET /projects/{course_slug}/{project_slug} -> ProjectDetail (brief, requirements, own submission, review history); 404 project_not_found
PUT /projects/{project_id}/submission {repo_url?, documentation_md?, reflection_md?, requirement_checks?} -> SubmissionRead (partial update; creates the draft)
  422 validation_error (bad GitHub link), 422 invalid_requirement, 422 repo_not_applicable, 409 submission_locked
POST /projects/{project_id}/submission/submit -> SubmissionRead; 409 no_draft, 409 submission_locked, 422 submission_incomplete (message lists what is missing)
GET /achievements -> 7 achievements with earned and earned_at (also records newly earned ones; repeating it changes nothing)

Staff only (instructor or admin; students get 403):
GET /reviews/queue?page=&page_size= -> submitted work, oldest first
GET /reviews/submissions/{submission_id} -> ReviewDetail; drafts return 404
POST /reviews/submissions/{submission_id} {outcome, rubric_scores {understanding, implementation, verification, ownership: 1..4}, feedback (10+ chars)} -> ReviewDetail
  403 cannot_review_own, 409 not_awaiting_review, 422 rubric_too_low (approval needs 2+ on every criterion), 404 submission_not_found

### Phase 7
Staff only (instructor or admin; others get 403) under /manage:
GET /manage/overview; GET /manage/students?page&page_size&q&role; GET /manage/students/{user_id}
PUT|DELETE /manage/students/{user_id}/enrollments/{course_slug} (PUT is idempotent and notifies the learner; DELETE keeps progress)
GET /manage/content; GET /manage/concepts
GET|PUT /manage/lessons/{id}; POST /manage/modules/{module_id}/lessons (409 slug_taken, 422 invalid_slug|unknown_concept|cannot_unpublish)
GET|POST /manage/lessons/{lesson_id}/exercises (409 lesson_unavailable|slug_taken, 422 invalid_definition|unknown_concept)
GET|PUT|DELETE /manage/exercises/{id} (DELETE: 409 has_submissions)
GET|PUT /manage/projects/{id}
Any signed-in user: GET /notifications, GET /notifications/unread-count, POST /notifications/{id}/read, POST /notifications/read-all (all filtered by owner).
