import json

import pytest
from sqlalchemy.orm import Session

from app.services.curriculum_loader import load_curriculum
from app.services.exercise_loader import load_exercises
from app.services.exercise_seed import seed_exercises
from app.services.project_loader import load_projects
from app.services.project_seed import seed_projects

API = "/api/v1"
QUIZ = {
    "slug": "quiz-one", "title": "Quiz", "kind": "quiz", "instructions": "Answer.", "concepts": ["logic"], "pass_score": 70,
    "questions": [{"id": "q1", "prompt": "2 + 2?", "options": ["3", "4"], "answer": 1, "explanation": "Four."}],
}
CODE = {
    "slug": "code-one", "title": "Code", "kind": "code", "instructions": "Print hi.", "concepts": ["logic"],
    "starter_code": "", "tests": [{"id": "t1", "description": "prints hi", "type": "stdout", "expected_stdout": "hi"}],
}
BUILD = {
    "title": "Build it", "summary": "Build.", "kind": "build", "concepts": ["logic"],
    "requirements": [{"id": "r1", "text": "Does a thing"}],
}
RUBRIC = {"understanding": 3, "implementation": 3, "verification": 3, "ownership": 3}


@pytest.fixture
def world(curriculum_root, db_engine, seed):
    folder = curriculum_root / "exercises" / "alpha" / "intro"
    folder.mkdir(parents=True)
    (folder / "one.json").write_text(json.dumps([QUIZ, CODE]))
    projects = curriculum_root / "projects" / "alpha"
    projects.mkdir(parents=True)
    (projects / "build-it.json").write_text(json.dumps(BUILD))
    (projects / "build-it.md").write_text("# Build\n\nBrief.")
    seed()
    data = load_curriculum(curriculum_root)
    with Session(db_engine) as session:
        seed_exercises(session, load_exercises(curriculum_root, data))
        seed_projects(session, load_projects(curriculum_root, data))
        session.commit()


def _lesson_ids(client, headers):
    course = client.get(f"{API}/courses/alpha", headers=headers).json()
    return {l["slug"]: l["id"] for m in course["modules"] for l in m["lessons"]}


def _finish_lessons(client, headers):
    for slug, lesson_id in _lesson_ids(client, headers).items():
        if slug in ("one", "two"):
            assert client.post(f"{API}/progress/lessons/{lesson_id}/complete", headers=headers).status_code == 200


def _pass_quiz(client, headers):
    lesson_id = _lesson_ids(client, headers)["one"]
    exercises = client.get(f"{API}/lessons/{lesson_id}/exercises", headers=headers).json()
    quiz = next(e for e in exercises if e["slug"] == "quiz-one")
    answer = {"answer": {"answers": {"q1": 1}}}
    assert client.post(f"{API}/exercises/{quiz['id']}/submissions", json=answer, headers=headers).json()["passed"] is True


def _approve_project(client, learner, teacher):
    headers = learner["headers"]
    project_id = client.get(f"{API}/projects", headers=headers).json()[0]["id"]
    draft = {"repo_url": "https://github.com/a/b", "documentation_md": "d" * 300, "reflection_md": "r" * 120, "requirement_checks": {"r1": True}}
    assert client.put(f"{API}/projects/{project_id}/submission", json=draft, headers=headers).status_code == 200
    assert client.post(f"{API}/projects/{project_id}/submission/submit", headers=headers).status_code == 200
    submission_id = client.get(f"{API}/projects/alpha/build-it", headers=headers).json()["submission"]["id"]
    review = {"outcome": "approved", "rubric_scores": RUBRIC, "feedback": "Solid work, well done."}
    assert client.post(f"{API}/reviews/submissions/{submission_id}", json=review, headers=teacher["headers"]).status_code == 200


def _alpha(client, headers):
    return next(c for c in client.get(f"{API}/certificates", headers=headers).json() if c["course_slug"] == "alpha")


def test_status_lists_requirements_and_blockers(client, make_user, world):
    user = make_user("a@example.com")
    listing = client.get(f"{API}/certificates", headers=user["headers"]).json()
    assert [c["course_slug"] for c in listing] == ["alpha", "beta"]
    alpha, beta = listing
    totals = {r["key"]: (r["done"], r["total"]) for r in alpha["requirements"]}
    assert totals == {"lessons": (0, 2), "exercises": (0, 1), "projects": (0, 1)}
    assert alpha["eligible"] is False and "Still to do" in alpha["message"] and alpha["certificate"] is None
    assert beta["eligible"] is False and "no reviewed project" in beta["message"]


def test_cannot_issue_before_meeting_the_requirements(client, make_user, world):
    user = make_user("a@example.com")
    response = client.post(f"{API}/certificates/alpha", headers=user["headers"])
    assert response.status_code == 409 and response.json()["error"]["code"] == "not_eligible"
    _finish_lessons(client, user["headers"])
    _pass_quiz(client, user["headers"])
    assert client.post(f"{API}/certificates/alpha", headers=user["headers"]).status_code == 409  # project still missing
    totals = {r["key"]: (r["done"], r["total"]) for r in _alpha(client, user["headers"])["requirements"]}
    assert totals == {"lessons": (2, 2), "exercises": (1, 1), "projects": (0, 1)}


def test_unknown_course_is_404(client, make_user, world):
    user = make_user("a@example.com")
    assert client.post(f"{API}/certificates/nope", headers=user["headers"]).status_code == 404


def test_full_flow_issue_verify_and_privacy(client, make_user, world):
    alice = make_user("alice@example.com")
    bob = make_user("bob@example.com")
    teacher = make_user("teacher@example.com", "instructor")
    _finish_lessons(client, alice["headers"])
    _pass_quiz(client, alice["headers"])
    _approve_project(client, alice, teacher)

    status = _alpha(client, alice["headers"])
    assert status["eligible"] is True and status["message"] is None

    issued = client.post(f"{API}/certificates/alpha", headers=alice["headers"])
    assert issued.status_code == 200
    body = issued.json()
    assert body["holder_name"] == "alice" and body["course_title"] == "Alpha" and len(body["code"]) >= 8
    again = client.post(f"{API}/certificates/alpha", headers=alice["headers"]).json()
    from datetime import datetime

    assert again["code"] == body["code"]
    assert datetime.fromisoformat(again["issued_at"]) == datetime.fromisoformat(body["issued_at"])
    assert _alpha(client, alice["headers"])["certificate"]["code"] == body["code"]

    public = client.get(f"{API}/certificates/verify/{body['code']}")  # no token needed
    assert public.status_code == 200 and public.json()["valid"] is True
    assert public.json()["holder_name"] == "alice" and public.json()["course_title"] == "Alpha"
    assert "@" not in public.text and "user_id" not in public.text

    assert _alpha(client, bob["headers"])["certificate"] is None
    notes = client.get(f"{API}/notifications", headers=alice["headers"]).json()
    assert any("Certificate issued" in item["title"] for item in notes["items"])


def test_code_exercises_never_block_a_certificate(client, make_user, world):
    user = make_user("a@example.com")
    totals = {r["key"]: r["total"] for r in _alpha(client, user["headers"])["requirements"]}
    assert totals["exercises"] == 1  # the quiz only; the code exercise is not counted


@pytest.mark.parametrize("code", ["abc", "does-not-exist-123", "..%2F..%2Fetc", "x" * 80])
def test_unknown_codes_are_404(client, code):
    response = client.get(f"{API}/certificates/verify/{code}")
    assert response.status_code == 404 and response.json()["error"]["code"] in ("certificate_not_found", "not_found")
