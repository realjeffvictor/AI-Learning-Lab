import pytest
from sqlalchemy import text

COURSES = "/api/v1/courses"
PROGRESS = "/api/v1/progress"


def _ids(client, headers) -> dict[str, str]:
    course = client.get(f"{COURSES}/alpha", headers=headers).json()
    return {lesson["slug"]: lesson["id"] for module in course["modules"] for lesson in module["lessons"]}


def _summary(client, headers) -> dict:
    return client.get(f"{PROGRESS}/summary", headers=headers).json()


def test_start_creates_progress_and_enrolls(client, make_user, seed):
    seed()
    user = make_user("a@example.com")
    ids = _ids(client, user["headers"])
    response = client.post(f"{PROGRESS}/lessons/{ids['one']}/start", headers=user["headers"])
    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"
    courses = client.get(COURSES, headers=user["headers"]).json()
    assert courses[0]["enrolled"] is True


def test_start_is_idempotent_and_never_downgrades(client, make_user, seed):
    seed()
    user = make_user("a@example.com")
    lesson_id = _ids(client, user["headers"])["one"]
    client.post(f"{PROGRESS}/lessons/{lesson_id}/complete", headers=user["headers"])
    again = client.post(f"{PROGRESS}/lessons/{lesson_id}/start", headers=user["headers"])
    assert again.json()["status"] == "completed"


def test_cannot_start_a_planned_lesson(client, make_user, seed):
    seed()
    user = make_user("a@example.com")
    planned = _ids(client, user["headers"])["three"]
    response = client.post(f"{PROGRESS}/lessons/{planned}/start", headers=user["headers"])
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "lesson_unavailable"


def test_start_unknown_lesson_is_404(client, make_user, seed):
    seed()
    user = make_user("a@example.com")
    response = client.post(
        f"{PROGRESS}/lessons/00000000-0000-4000-8000-000000000000/start", headers=user["headers"]
    )
    assert response.status_code == 404


def test_time_requires_a_started_lesson(client, make_user, seed):
    seed()
    user = make_user("a@example.com")
    lesson_id = _ids(client, user["headers"])["one"]
    response = client.post(f"{PROGRESS}/lessons/{lesson_id}/time", json={"seconds": 10}, headers=user["headers"])
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "progress_not_started"


def test_time_claims_are_capped_by_wall_clock(client, make_user, seed):
    seed()
    user = make_user("a@example.com")
    lesson_id = _ids(client, user["headers"])["one"]
    client.post(f"{PROGRESS}/lessons/{lesson_id}/start", headers=user["headers"])
    response = client.post(f"{PROGRESS}/lessons/{lesson_id}/time", json={"seconds": 120}, headers=user["headers"])
    assert response.status_code == 200
    assert response.json()["time_spent_seconds"] <= 7


def test_time_is_credited_when_it_really_elapsed(client, make_user, seed, db_engine):
    seed()
    user = make_user("a@example.com")
    lesson_id = _ids(client, user["headers"])["one"]
    client.post(f"{PROGRESS}/lessons/{lesson_id}/start", headers=user["headers"])
    with db_engine.begin() as connection:
        connection.execute(text("UPDATE lesson_progress SET last_visited_at = last_visited_at - interval '60 seconds'"))
    response = client.post(f"{PROGRESS}/lessons/{lesson_id}/time", json={"seconds": 30}, headers=user["headers"])
    assert response.json()["time_spent_seconds"] == 30


@pytest.mark.parametrize("seconds", [0, 121, -5])
def test_time_amount_is_validated(client, make_user, seed, seconds):
    seed()
    user = make_user("a@example.com")
    lesson_id = _ids(client, user["headers"])["one"]
    response = client.post(f"{PROGRESS}/lessons/{lesson_id}/time", json={"seconds": seconds}, headers=user["headers"])
    assert response.status_code == 422


def test_complete_marks_progress_and_records_competency_exposure(client, make_user, seed):
    seed()
    user = make_user("a@example.com")
    lesson_id = _ids(client, user["headers"])["one"]
    response = client.post(f"{PROGRESS}/lessons/{lesson_id}/complete", headers=user["headers"])
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed" and body["completed_at"] is not None
    competencies = {c["slug"]: c["lessons_completed"] for c in _summary(client, user["headers"])["competencies"]}
    assert competencies == {"logic": 1, "loops": 1}


def test_completing_twice_does_not_double_count(client, make_user, seed):
    seed()
    user = make_user("a@example.com")
    lesson_id = _ids(client, user["headers"])["one"]
    client.post(f"{PROGRESS}/lessons/{lesson_id}/complete", headers=user["headers"])
    client.post(f"{PROGRESS}/lessons/{lesson_id}/complete", headers=user["headers"])
    summary = _summary(client, user["headers"])
    assert summary["lessons_completed"] == 1
    assert {c["slug"]: c["lessons_completed"] for c in summary["competencies"]}["logic"] == 1


def test_exposure_accumulates_across_lessons(client, make_user, seed):
    seed()
    user = make_user("a@example.com")
    ids = _ids(client, user["headers"])
    client.post(f"{PROGRESS}/lessons/{ids['one']}/complete", headers=user["headers"])
    client.post(f"{PROGRESS}/lessons/{ids['two']}/complete", headers=user["headers"])
    competencies = {c["slug"]: c["lessons_completed"] for c in _summary(client, user["headers"])["competencies"]}
    assert competencies == {"logic": 2, "loops": 1}


def test_complete_without_start_works_and_enrolls(client, make_user, seed):
    seed()
    user = make_user("a@example.com")
    lesson_id = _ids(client, user["headers"])["two"]
    assert client.post(f"{PROGRESS}/lessons/{lesson_id}/complete", headers=user["headers"]).status_code == 200
    assert client.get(COURSES, headers=user["headers"]).json()[0]["enrolled"] is True


def test_cannot_complete_a_planned_lesson(client, make_user, seed):
    seed()
    user = make_user("a@example.com")
    planned = _ids(client, user["headers"])["three"]
    response = client.post(f"{PROGRESS}/lessons/{planned}/complete", headers=user["headers"])
    assert response.status_code == 409


def test_up_next_follows_the_learner(client, make_user, seed):
    seed()
    user = make_user("a@example.com")
    ids = _ids(client, user["headers"])
    headers = user["headers"]

    first = _summary(client, headers)["up_next"]
    assert (first["reason"], first["lesson_slug"]) == ("start", "one")

    client.post(f"{PROGRESS}/lessons/{ids['one']}/start", headers=headers)
    second = _summary(client, headers)["up_next"]
    assert (second["reason"], second["lesson_slug"]) == ("continue", "one")

    client.post(f"{PROGRESS}/lessons/{ids['one']}/complete", headers=headers)
    third = _summary(client, headers)["up_next"]
    assert (third["reason"], third["lesson_slug"]) == ("start", "two")

    client.post(f"{PROGRESS}/lessons/{ids['two']}/complete", headers=headers)
    assert _summary(client, headers)["up_next"] is None


def test_progress_is_private_per_user(client, make_user, seed):
    seed()
    alice = make_user("alice@example.com")
    bob = make_user("bob@example.com")
    lesson_id = _ids(client, alice["headers"])["one"]
    client.post(f"{PROGRESS}/lessons/{lesson_id}/complete", headers=alice["headers"])
    summary = _summary(client, bob["headers"])
    assert summary["lessons_completed"] == 0 and summary["competencies"] == []
    course = client.get(f"{COURSES}/alpha", headers=bob["headers"]).json()
    assert course["modules"][0]["lessons"][0]["progress"] == "not_started"


def test_course_detail_reflects_completion(client, make_user, seed):
    seed()
    user = make_user("a@example.com")
    lesson_id = _ids(client, user["headers"])["one"]
    client.post(f"{PROGRESS}/lessons/{lesson_id}/complete", headers=user["headers"])
    course = client.get(f"{COURSES}/alpha", headers=user["headers"]).json()
    assert course["modules"][0]["lessons"][0]["progress"] == "completed"
    assert course["completed_lesson_count"] == 1
