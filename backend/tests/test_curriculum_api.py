BASE = "/api/v1/courses"


def _lesson_ids(client, headers) -> dict[str, str]:
    course = client.get(f"{BASE}/alpha", headers=headers).json()
    return {lesson["slug"]: lesson["id"] for module in course["modules"] for lesson in module["lessons"]}


def test_courses_require_authentication(client):
    assert client.get(BASE).status_code == 401


def test_list_courses(client, make_user, seed):
    seed()
    user = make_user("a@example.com")
    body = client.get(BASE, headers=user["headers"]).json()
    assert [c["slug"] for c in body] == ["alpha", "beta"]
    alpha = body[0]
    assert (alpha["module_count"], alpha["published_lesson_count"], alpha["planned_lesson_count"]) == (2, 2, 1)
    assert alpha["enrolled"] is False and alpha["completed_lesson_count"] == 0
    assert body[1]["kind"] == "track" and body[1]["stage_number"] is None


def test_course_detail_shows_modules_and_honest_status(client, make_user, seed):
    seed()
    user = make_user("a@example.com")
    course = client.get(f"{BASE}/alpha", headers=user["headers"]).json()
    intro, empty = course["modules"]
    assert intro["status"] == "published" and empty["status"] == "planned"
    assert [lesson["status"] for lesson in intro["lessons"]] == ["published", "published", "planned"]
    assert all(lesson["progress"] == "not_started" for lesson in intro["lessons"])
    assert empty["lessons"] == []


def test_unknown_course_is_404(client, make_user, seed):
    seed()
    user = make_user("a@example.com")
    response = client.get(f"{BASE}/nope", headers=user["headers"])
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "course_not_found"


def test_published_lesson_detail(client, make_user, seed):
    seed()
    user = make_user("a@example.com")
    body = client.get(f"{BASE}/alpha/modules/intro/lessons/one", headers=user["headers"]).json()
    assert body["status"] == "published"
    assert body["content_md"].startswith("## One")
    assert {c["slug"] for c in body["concepts"]} == {"logic", "loops"}
    assert body["objectives"] == ["Do a thing"]
    assert body["previous"] is None
    assert body["next"]["slug"] == "two"
    assert body["progress"]["status"] == "not_started"


def test_planned_lesson_has_no_content_or_navigation(client, make_user, seed):
    seed()
    user = make_user("a@example.com")
    body = client.get(f"{BASE}/alpha/modules/intro/lessons/three", headers=user["headers"]).json()
    assert body["status"] == "planned"
    assert body["content_md"] is None
    assert body["previous"] is None and body["next"] is None


def test_unknown_lesson_is_404(client, make_user, seed):
    seed()
    user = make_user("a@example.com")
    response = client.get(f"{BASE}/alpha/modules/intro/lessons/nope", headers=user["headers"])
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "lesson_not_found"


def test_enrollment_is_idempotent(client, make_user, seed):
    seed()
    user = make_user("a@example.com")
    first = client.post(f"{BASE}/alpha/enrollment", headers=user["headers"])
    second = client.post(f"{BASE}/alpha/enrollment", headers=user["headers"])
    assert first.status_code == second.status_code == 200
    assert first.json()["enrolled_at"] == second.json()["enrolled_at"]
    listing = client.get(BASE, headers=user["headers"]).json()
    assert [c["enrolled"] for c in listing] == [True, False]


def test_enrolling_in_unknown_course_is_404(client, make_user, seed):
    seed()
    user = make_user("a@example.com")
    assert client.post(f"{BASE}/nope/enrollment", headers=user["headers"]).status_code == 404
