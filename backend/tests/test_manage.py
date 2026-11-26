import json
import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.curriculum_loader import load_curriculum
from app.services.project_loader import load_projects
from app.services.project_seed import seed_projects

API = "/api/v1"
M = f"{API}/manage"
MISSING = "00000000-0000-4000-8000-000000000000"
QUIZ_DEF = {
    "questions": [
        {"id": "q1", "prompt": "2 + 2?", "options": ["3", "4"], "answer": 1, "explanation": "Four.", "concept": "logic"}
    ]
}
BUILD = {
    "title": "Build it", "summary": "Build.", "kind": "build", "concepts": ["logic"],
    "requirements": [{"id": "r1", "text": "Does a thing"}],
}


def lesson_body(**overrides):
    body = {
        "title": "New lesson", "summary": "S", "minutes": 7, "objectives": ["Do it"],
        "principles": ["U", "V"], "concepts": ["logic"], "content_md": "## Hello\n\nBody.",
    }
    body.update(overrides)
    return body


def exercise_body(**overrides):
    body = {
        "slug": "quiz-a", "kind": "quiz", "title": "Quiz A", "instructions_md": "Answer it.",
        "pass_score": 70, "concepts": ["logic"], "definition": QUIZ_DEF,
    }
    body.update(overrides)
    return body


def ids(client, headers):
    tree = client.get(f"{M}/content", headers=headers).json()
    course = next(c for c in tree["courses"] if c["slug"] == "alpha")
    modules = {m["slug"]: m for m in course["modules"]}
    lessons = {l["slug"]: l["id"] for l in modules["intro"]["lessons"]}
    return modules["intro"]["id"], lessons


@pytest.fixture
def teacher(make_user):
    return make_user("teacher@example.com", "instructor")


@pytest.fixture
def project_seeded(curriculum_root, db_engine, seed):
    folder = curriculum_root / "projects" / "alpha"
    folder.mkdir(parents=True)
    (folder / "build-it.json").write_text(json.dumps(BUILD))
    (folder / "build-it.md").write_text("# Build it\n\nBrief.")
    seed()
    with Session(db_engine) as session:
        seed_projects(session, load_projects(curriculum_root, load_curriculum(curriculum_root)))
        session.commit()


# ------------------------------------------------------------------ authorization
@pytest.mark.parametrize("path", ["/overview", "/students", "/content", "/concepts", f"/lessons/{MISSING}"])
def test_read_endpoints_are_staff_only(client, make_user, path):
    student = make_user("student@example.com")
    staff = make_user("teacher@example.com", "instructor")
    admin = make_user("admin@example.com", "admin")
    assert client.get(M + path).status_code == 401
    assert client.get(M + path, headers=student["headers"]).status_code == 403
    assert client.get(M + path, headers=staff["headers"]).status_code != 403
    assert client.get(M + path, headers=admin["headers"]).status_code != 403


def test_write_endpoints_are_staff_only(client, make_user):
    student = make_user("student@example.com")
    h = student["headers"]
    assert client.post(f"{M}/modules/{MISSING}/lessons", json={**lesson_body(), "slug": "x"}, headers=h).status_code == 403
    assert client.put(f"{M}/lessons/{MISSING}", json=lesson_body(), headers=h).status_code == 403
    assert client.post(f"{M}/lessons/{MISSING}/exercises", json=exercise_body(), headers=h).status_code == 403
    assert client.delete(f"{M}/exercises/{MISSING}", headers=h).status_code == 403
    assert client.put(f"{M}/projects/{MISSING}", json={"title": "t", "brief_md": "b"}, headers=h).status_code == 403
    assert client.put(f"{M}/students/{student['id']}/enrollments/alpha", headers=h).status_code == 403
    assert client.delete(f"{M}/students/{student['id']}/enrollments/alpha", headers=h).status_code == 403


# ------------------------------------------------------------------ analytics and students
def test_overview(client, make_user, seed, teacher):
    seed()
    make_user("a@example.com")
    body = client.get(f"{M}/overview", headers=teacher["headers"]).json()
    assert body["users_by_role"] == {"student": 1, "instructor": 1}
    assert body["pending_reviews"] == 0 and body["ai"]["requests_today"] == 0
    assert [e["course_slug"] for e in body["enrollments"]] == ["alpha", "beta"]
    assert body["top_lessons"] == [] and body["exercises"] == []


def test_overview_counts_completions_and_activity(client, make_user, seed, teacher):
    seed()
    alice = make_user("alice@example.com")
    _module, lessons = ids(client, teacher["headers"])
    assert client.post(f"{API}/progress/lessons/{lessons['one']}/complete", headers=alice["headers"]).status_code == 200
    body = client.get(f"{M}/overview", headers=teacher["headers"]).json()
    assert body["active_learners_7d"] == 1
    assert body["top_lessons"][0]["lesson_slug"] == "one" and body["top_lessons"][0]["completed"] == 1


def test_student_list_search_filter_and_paging(client, make_user, teacher):
    make_user("ada@example.com")
    make_user("grace@example.com")
    headers = teacher["headers"]
    everyone = client.get(f"{M}/students", headers=headers).json()
    assert everyone["total"] == 3
    assert [r["email"] for r in client.get(f"{M}/students?q=ADA", headers=headers).json()["items"]] == ["ada@example.com"]
    assert client.get(f"{M}/students?role=instructor", headers=headers).json()["total"] == 1
    assert client.get(f"{M}/students?q=zzz_", headers=headers).json()["total"] == 0
    assert client.get(f"{M}/students?q=%25", headers=headers).json()["total"] == 0
    assert len(client.get(f"{M}/students?page=1&page_size=2", headers=headers).json()["items"]) == 2
    assert client.get(f"{M}/students?page_size=500", headers=headers).status_code == 422
    assert client.get(f"{M}/students?role=root", headers=headers).status_code == 422


def test_student_detail(client, make_user, seed, teacher):
    seed()
    alice = make_user("alice@example.com")
    _module, lessons = ids(client, teacher["headers"])
    client.post(f"{API}/progress/lessons/{lessons['one']}/complete", headers=alice["headers"])
    body = client.get(f"{M}/students/{alice['id']}", headers=teacher["headers"]).json()
    assert body["user"]["email"] == "alice@example.com" and body["lessons_completed"] == 1
    assert body["exercise_attempts"] == 0 and [c["slug"] for c in body["courses"]] == ["alpha", "beta"]
    assert body["courses"][0]["enrolled"] is True and body["projects"] == [] and body["mastery"] == []
    assert client.get(f"{M}/students/{MISSING}", headers=teacher["headers"]).status_code == 404


def test_enrollment_management_and_notification(client, make_user, seed, teacher):
    seed()
    alice = make_user("alice@example.com")
    url = f"{M}/students/{alice['id']}/enrollments/alpha"
    first = client.put(url, headers=teacher["headers"])
    second = client.put(url, headers=teacher["headers"])
    assert first.status_code == second.status_code == 200
    assert first.json()["enrolled_at"] == second.json()["enrolled_at"]
    notes = client.get(f"{API}/notifications", headers=alice["headers"]).json()
    assert notes["unread_count"] == 1 and notes["items"][0]["link"] == "/courses/alpha"
    assert client.get(f"{API}/courses", headers=alice["headers"]).json()[0]["enrolled"] is True

    assert client.delete(url, headers=teacher["headers"]).status_code == 204
    assert client.delete(url, headers=teacher["headers"]).status_code == 204
    assert client.get(f"{API}/courses", headers=alice["headers"]).json()[0]["enrolled"] is False
    assert client.put(f"{M}/students/{alice['id']}/enrollments/nope", headers=teacher["headers"]).status_code == 404
    assert client.put(f"{M}/students/{MISSING}/enrollments/alpha", headers=teacher["headers"]).status_code == 404


# ------------------------------------------------------------------ lessons
def test_content_tree(client, seed, teacher):
    seed()
    tree = client.get(f"{M}/content", headers=teacher["headers"]).json()
    assert [c["slug"] for c in tree["courses"]] == ["alpha", "beta"]
    intro = tree["courses"][0]["modules"][0]
    assert [(l["slug"], l["status"], l["managed_in_app"]) for l in intro["lessons"]] == [
        ("one", "published", False), ("two", "published", False), ("three", "planned", False)
    ]


def test_create_lesson_and_learner_sees_it(client, make_user, seed, teacher):
    seed()
    module_id, _lessons = ids(client, teacher["headers"])
    response = client.post(f"{M}/modules/{module_id}/lessons", json={**lesson_body(), "slug": "fresh"}, headers=teacher["headers"])
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "published" and body["managed_in_app"] is True and body["concepts"] == ["logic"]
    assert body["module_slug"] == "intro" and body["course_slug"] == "alpha"
    learner = make_user("a@example.com")
    lesson = client.get(f"{API}/courses/alpha/modules/intro/lessons/fresh", headers=learner["headers"]).json()
    assert lesson["status"] == "published" and lesson["content_md"].startswith("## Hello")
    assert lesson["principles"] == ["U", "V"] and lesson["objectives"] == ["Do it"]


def test_new_lesson_without_content_is_planned(client, make_user, seed, teacher):
    seed()
    module_id, _ = ids(client, teacher["headers"])
    body = client.post(
        f"{M}/modules/{module_id}/lessons", json={**lesson_body(content_md="  "), "slug": "later"}, headers=teacher["headers"]
    ).json()
    assert body["status"] == "planned" and body["content_md"] is None
    learner = make_user("a@example.com")
    assert client.get(f"{API}/courses/alpha/modules/intro/lessons/later", headers=learner["headers"]).json()["content_md"] is None
    response = client.post(f"{M}/lessons/{body['id']}/exercises", json=exercise_body(), headers=teacher["headers"])
    assert response.status_code == 409 and response.json()["error"]["code"] == "lesson_unavailable"


@pytest.mark.parametrize(
    ("overrides", "status"),
    [
        ({"slug": "Bad Slug"}, 422), ({"slug": "one"}, 409), ({"concepts": ["nope"]}, 422),
        ({"principles": ["X"]}, 422), ({"minutes": 0}, 422), ({"objectives": ["x"] * 9}, 422),
        ({"title": "   "}, 422), ({"concepts": ["logic", "logic"]}, 422), ({"extra": 1}, 422),
    ],
)
def test_create_lesson_validation(client, seed, teacher, overrides, status):
    seed()
    module_id, _ = ids(client, teacher["headers"])
    body = {**lesson_body(), "slug": "fresh", **overrides}
    assert client.post(f"{M}/modules/{module_id}/lessons", json=body, headers=teacher["headers"]).status_code == status


def test_create_lesson_in_unknown_module(client, teacher):
    response = client.post(f"{M}/modules/{MISSING}/lessons", json={**lesson_body(), "slug": "x"}, headers=teacher["headers"])
    assert response.status_code == 404 and response.json()["error"]["code"] == "module_not_found"


def test_update_lesson_and_publish_a_planned_one(client, make_user, seed, teacher):
    seed()
    _module, lessons = ids(client, teacher["headers"])
    edited = client.put(f"{M}/lessons/{lessons['one']}", json=lesson_body(title="Renamed", concepts=["loops"]), headers=teacher["headers"])
    assert edited.status_code == 200 and edited.json()["title"] == "Renamed" and edited.json()["concepts"] == ["loops"]
    published = client.put(f"{M}/lessons/{lessons['three']}", json=lesson_body(), headers=teacher["headers"]).json()
    assert published["status"] == "published"
    learner = make_user("a@example.com")
    course = client.get(f"{API}/courses/alpha", headers=learner["headers"]).json()
    assert [l["status"] for l in course["modules"][0]["lessons"]] == ["published"] * 3


def test_published_lessons_cannot_be_emptied(client, seed, teacher):
    seed()
    _module, lessons = ids(client, teacher["headers"])
    response = client.put(f"{M}/lessons/{lessons['one']}", json=lesson_body(content_md=""), headers=teacher["headers"])
    assert response.status_code == 422 and response.json()["error"]["code"] == "cannot_unpublish"
    assert client.get(f"{M}/lessons/{lessons['one']}", headers=teacher["headers"]).json()["content_md"].startswith("## One")


def test_content_edits_are_audited(client, seed, teacher, db_engine):
    seed()
    module_id, lessons = ids(client, teacher["headers"])
    client.post(f"{M}/modules/{module_id}/lessons", json={**lesson_body(), "slug": "fresh"}, headers=teacher["headers"])
    client.put(f"{M}/lessons/{lessons['one']}", json=lesson_body(), headers=teacher["headers"])
    with db_engine.connect() as connection:
        actions = {r[0] for r in connection.execute(text("SELECT action FROM audit_logs WHERE action LIKE 'content.%'"))}
    assert actions == {"content.lesson_created", "content.lesson_updated"}


def test_seed_does_not_overwrite_lessons_edited_in_the_app(client, seed, teacher, curriculum_root, db_engine):
    seed()
    _module, lessons = ids(client, teacher["headers"])
    client.put(f"{M}/lessons/{lessons['one']}", json=lesson_body(title="Edited in the app"), headers=teacher["headers"])
    path = curriculum_root / "courses" / "01-alpha" / "course.json"
    data = json.loads(path.read_text())
    data["modules"][0]["lessons"][0]["title"] = "Changed in the file"
    path.write_text(json.dumps(data))
    report = seed()
    assert any("one" in o and "edited in the app" in o for o in report.orphans)
    assert client.get(f"{M}/lessons/{lessons['one']}", headers=teacher["headers"]).json()["title"] == "Edited in the app"


# ------------------------------------------------------------------ exercises
def test_exercise_lifecycle(client, make_user, seed, teacher):
    seed()
    _module, lessons = ids(client, teacher["headers"])
    lesson_id = lessons["one"]
    created = client.post(f"{M}/lessons/{lesson_id}/exercises", json=exercise_body(), headers=teacher["headers"])
    assert created.status_code == 201
    exercise = created.json()
    assert exercise["managed_in_app"] is True and exercise["attempts"] == 0 and exercise["concepts"] == ["logic"]
    assert client.get(f"{M}/lessons/{lesson_id}/exercises", headers=teacher["headers"]).json()[0]["id"] == exercise["id"]

    learner = make_user("a@example.com")
    visible = client.get(f"{API}/lessons/{lesson_id}/exercises", headers=learner["headers"]).json()
    assert [e["slug"] for e in visible] == ["quiz-a"] and '"answer"' not in json.dumps(visible)

    changed = {**QUIZ_DEF, "questions": [{**QUIZ_DEF["questions"][0], "prompt": "Two plus two?"}]}
    update = {"title": "Quiz A2", "instructions_md": "New text", "pass_score": 80, "concepts": ["logic", "loops"], "definition": changed}
    updated = client.put(f"{M}/exercises/{exercise['id']}", json=update, headers=teacher["headers"]).json()
    assert updated["title"] == "Quiz A2" and updated["pass_score"] == 80 and set(updated["concepts"]) == {"logic", "loops"}

    answer = {"answer": {"answers": {"q1": 1}}}
    assert client.post(f"{API}/exercises/{exercise['id']}/submissions", json=answer, headers=learner["headers"]).json()["score"] == 100
    refused = client.delete(f"{M}/exercises/{exercise['id']}", headers=teacher["headers"])
    assert refused.status_code == 409 and refused.json()["error"]["code"] == "has_submissions"

    other = client.post(f"{M}/lessons/{lesson_id}/exercises", json=exercise_body(slug="quiz-b"), headers=teacher["headers"]).json()
    assert other["attempts"] == 0
    assert client.delete(f"{M}/exercises/{other['id']}", headers=teacher["headers"]).status_code == 204
    assert client.get(f"{M}/exercises/{other['id']}", headers=teacher["headers"]).status_code == 404


@pytest.mark.parametrize(
    "definition",
    [
        {}, {"questions": []},
        {"questions": [{"id": "q1", "prompt": "p", "options": ["a", "b"], "answer": 5, "explanation": "e"}]},
        {"questions": [{"id": "q1", "prompt": "p", "options": ["a", "b"], "answer": 0, "explanation": "e", "concept": "loops"}]},
        {"questions": [{"id": "q1", "prompt": "p", "options": ["a", "b"], "answer": 0, "explanation": "e", "concept": ["x"]}]},
        {"questions": "nope"},
    ],
)
def test_invalid_quiz_definitions_are_rejected(client, seed, teacher, definition):
    seed()
    _module, lessons = ids(client, teacher["headers"])
    response = client.post(
        f"{M}/lessons/{lessons['one']}/exercises", json=exercise_body(definition=definition), headers=teacher["headers"]
    )
    assert response.status_code == 422 and response.json()["error"]["code"] == "invalid_definition"


def test_code_and_puzzle_exercises_use_their_own_rules(client, seed, teacher):
    seed()
    _module, lessons = ids(client, teacher["headers"])
    url = f"{M}/lessons/{lessons['one']}/exercises"
    code = {"starter_code": "", "timeout_seconds": 5, "tests": [{"id": "t1", "description": "hi", "type": "stdout", "expected_stdout": "hi"}]}
    assert client.post(url, json=exercise_body(slug="code-a", kind="code", definition=code), headers=teacher["headers"]).status_code == 201
    bad_code = {**code, "timeout_seconds": 99}
    assert client.post(url, json=exercise_body(slug="code-b", kind="code", definition=bad_code), headers=teacher["headers"]).status_code == 422
    puzzle = {"puzzle_type": "order", "lines": ["a = 1", "b = 2"]}
    assert client.post(url, json=exercise_body(slug="puz-a", kind="puzzle", definition=puzzle), headers=teacher["headers"]).status_code == 201
    dup = {"puzzle_type": "order", "lines": ["a", "a"]}
    assert client.post(url, json=exercise_body(slug="puz-b", kind="puzzle", definition=dup), headers=teacher["headers"]).status_code == 422
    assert client.post(url, json=exercise_body(slug="quiz-a"), headers=teacher["headers"]).status_code == 201
    assert client.post(url, json=exercise_body(slug="quiz-a"), headers=teacher["headers"]).status_code == 409
    assert client.post(url, json=exercise_body(slug="Bad Slug"), headers=teacher["headers"]).status_code == 422
    assert client.post(url, json=exercise_body(slug="x", concepts=["nope"]), headers=teacher["headers"]).status_code == 422
    assert client.post(url, json=exercise_body(slug="y", concepts=[]), headers=teacher["headers"]).status_code == 422


# ------------------------------------------------------------------ projects and notifications
def test_project_editing(client, make_user, project_seeded, teacher):
    learner = make_user("a@example.com")
    project_id = client.get(f"{API}/projects", headers=learner["headers"]).json()[0]["id"]
    body = client.get(f"{M}/projects/{project_id}", headers=teacher["headers"]).json()
    assert body["title"] == "Build it" and body["managed_in_app"] is False and body["requirements"][0]["id"] == "r1"
    update = {"title": "Build it better", "summary": "New summary", "brief_md": "# New brief"}
    assert client.put(f"{M}/projects/{project_id}", json=update, headers=teacher["headers"]).json()["managed_in_app"] is True
    shown = client.get(f"{API}/projects/alpha/build-it", headers=learner["headers"]).json()
    assert shown["title"] == "Build it better" and shown["brief_md"] == "# New brief"
    assert client.put(f"{M}/projects/{project_id}", json={**update, "title": " "}, headers=teacher["headers"]).status_code == 422
    assert client.get(f"{M}/projects/{MISSING}", headers=teacher["headers"]).status_code == 404


def test_review_notifies_the_learner(client, make_user, project_seeded, teacher):
    alice = make_user("alice@example.com")
    project_id = client.get(f"{API}/projects", headers=alice["headers"]).json()[0]["id"]
    draft = {"repo_url": "https://github.com/alice/x", "documentation_md": "d" * 300, "reflection_md": "r" * 120, "requirement_checks": {"r1": True}}
    assert client.put(f"{API}/projects/{project_id}/submission", json=draft, headers=alice["headers"]).status_code == 200
    assert client.post(f"{API}/projects/{project_id}/submission/submit", headers=alice["headers"]).status_code == 200
    submission_id = client.get(f"{API}/projects/alpha/build-it", headers=alice["headers"]).json()["submission"]["id"]
    review = {
        "outcome": "changes_requested",
        "rubric_scores": {"understanding": 2, "implementation": 2, "verification": 1, "ownership": 2},
        "feedback": "Please add tests.",
    }
    assert client.post(f"{API}/reviews/submissions/{submission_id}", json=review, headers=teacher["headers"]).status_code == 200
    notes = client.get(f"{API}/notifications", headers=alice["headers"]).json()
    assert notes["unread_count"] == 1
    assert "Changes requested" in notes["items"][0]["title"] and notes["items"][0]["link"] == "/projects/alpha/build-it"
    assert client.get(f"{API}/notifications", headers=teacher["headers"]).json()["items"] == []


def test_notifications_read_state_and_privacy(client, make_user, seed, teacher):
    seed()
    alice = make_user("alice@example.com")
    bob = make_user("bob@example.com")
    client.put(f"{M}/students/{alice['id']}/enrollments/alpha", headers=teacher["headers"])
    client.put(f"{M}/students/{alice['id']}/enrollments/beta", headers=teacher["headers"])
    assert client.get(f"{API}/notifications/unread-count", headers=alice["headers"]).json() == {"unread_count": 2}
    items = client.get(f"{API}/notifications", headers=alice["headers"]).json()["items"]
    assert len(items) == 2
    assert client.post(f"{API}/notifications/{items[0]['id']}/read", headers=bob["headers"]).status_code == 404
    assert client.post(f"{API}/notifications/{items[0]['id']}/read", headers=alice["headers"]).status_code == 204
    assert client.post(f"{API}/notifications/{items[0]['id']}/read", headers=alice["headers"]).status_code == 204
    assert client.get(f"{API}/notifications/unread-count", headers=alice["headers"]).json()["unread_count"] == 1
    assert client.get(f"{API}/notifications", headers=bob["headers"]).json() == {"items": [], "unread_count": 0}
    assert client.post(f"{API}/notifications/read-all", headers=alice["headers"]).status_code == 204
    assert client.get(f"{API}/notifications/unread-count", headers=alice["headers"]).json()["unread_count"] == 0
    assert client.post(f"{API}/notifications/{uuid.uuid4()}/read", headers=alice["headers"]).status_code == 404
    assert client.get(f"{API}/notifications").status_code == 401
