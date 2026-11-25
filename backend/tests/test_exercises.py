import json
from pathlib import Path

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Exercise, Resource
from app.services.curriculum_loader import CurriculumError, load_curriculum
from app.services.exercise_loader import load_exercises
from app.services.exercise_seed import seed_exercises

COURSES = "/api/v1/courses"
API = "/api/v1"

SAMPLE_EXERCISES = [
    {
        "slug": "quiz-one", "title": "Quick check", "kind": "quiz", "instructions": "Answer both.",
        "concepts": ["logic", "loops"], "pass_score": 70,
        "questions": [
            {"id": "q1", "prompt": "2 + 2?", "options": ["3", "4"], "answer": 1, "explanation": "Four.", "concept": "logic"},
            {"id": "q2", "prompt": "Repeating work uses?", "options": ["a loop", "print"], "answer": 0, "explanation": "Loops."},
        ],
    },
    {
        "slug": "code-one", "title": "Double", "kind": "code", "instructions": "Write double(n).", "concepts": ["logic"],
        "starter_code": "def double(n):\n    pass\n",
        "tests": [
            {"id": "t1", "description": "double(4) is 8", "type": "return", "call": "double(4)", "expected": 8},
            {"id": "t2", "description": "prints hi", "type": "stdout", "expected_stdout": "hi"},
        ],
    },
    {
        "slug": "puzzle-one", "title": "Order", "kind": "puzzle", "instructions": "Order the lines.", "concepts": ["logic"],
        "puzzle_type": "order", "lines": ["a = 1", "b = 2", "c = a + b"],
    },
]
SAMPLE_RESOURCES = [
    {"title": "Logic primer", "url": "https://example.com/logic", "kind": "article", "concept": "logic",
     "level": "beginner", "is_open_source": True},
]


def write_exercises(root: Path, exercises=None, resources=None, lesson: str = "one") -> None:
    folder = root / "exercises" / "alpha" / "intro"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{lesson}.json").write_text(json.dumps(SAMPLE_EXERCISES if exercises is None else exercises))
    (root / "resources.json").write_text(json.dumps(SAMPLE_RESOURCES if resources is None else resources))


@pytest.fixture
def seed_all(curriculum_root, db_engine, seed):
    write_exercises(curriculum_root)
    seed()
    data = load_curriculum(curriculum_root)
    bundle = load_exercises(curriculum_root, data)
    with Session(db_engine) as session:
        report = seed_exercises(session, bundle)
        session.commit()
    return report


def _lesson_id(client, headers, slug="one") -> str:
    course = client.get(f"{COURSES}/alpha", headers=headers).json()
    return {lesson["slug"]: lesson["id"] for module in course["modules"] for lesson in module["lessons"]}[slug]


def _exercises(client, headers) -> dict:
    listing = client.get(f"{API}/lessons/{_lesson_id(client, headers)}/exercises", headers=headers).json()
    return {item["slug"]: item for item in listing}


def _quiz(client, headers, answers):
    exercise = _exercises(client, headers)["quiz-one"]
    return client.post(f"{API}/exercises/{exercise['id']}/submissions", json={"answer": {"answers": answers}}, headers=headers)


def test_requires_authentication(client, seed_all):
    assert client.get(f"{API}/assessments/mastery").status_code == 401


def test_exercises_hide_answers(client, make_user, seed_all):
    user = make_user("a@example.com")
    exercises = _exercises(client, user["headers"])
    assert list(exercises) == ["quiz-one", "code-one", "puzzle-one"]
    quiz_text = json.dumps(exercises["quiz-one"])
    assert '"answer"' not in quiz_text and "Four." not in quiz_text
    puzzle = exercises["puzzle-one"]["definition"]
    assert "lines" not in puzzle and [i["id"] for i in puzzle["items"]] != ["i0", "i1", "i2"]
    assert {i["id"] for i in puzzle["items"]} == {"i0", "i1", "i2"}
    assert exercises["code-one"]["definition"]["tests"][0]["expected"] == 8
    assert exercises["quiz-one"]["attempts"] == 0 and exercises["quiz-one"]["best_score"] is None


def test_planned_lesson_has_no_exercises(client, make_user, seed_all):
    user = make_user("a@example.com")
    lesson_id = _lesson_id(client, user["headers"], "three")
    assert client.get(f"{API}/lessons/{lesson_id}/exercises", headers=user["headers"]).json() == []


def test_unknown_lesson_and_exercise_are_404(client, make_user, seed_all):
    user = make_user("a@example.com")
    missing = "00000000-0000-4000-8000-000000000000"
    assert client.get(f"{API}/lessons/{missing}/exercises", headers=user["headers"]).status_code == 404
    response = client.post(f"{API}/exercises/{missing}/submissions", json={"answer": {}}, headers=user["headers"])
    assert response.status_code == 404 and response.json()["error"]["code"] == "exercise_not_found"
    assert client.get(f"{API}/exercises/{missing}/submissions", headers=user["headers"]).status_code == 404


def test_perfect_quiz_passes_with_no_recommendations(client, make_user, seed_all):
    user = make_user("a@example.com")
    body = _quiz(client, user["headers"], {"q1": 1, "q2": 0}).json()
    assert body["score"] == 100 and body["passed"] is True and body["attempt_number"] == 1
    results = {c["slug"]: (c["correct"], c["total"]) for c in body["concept_results"]}
    assert results == {"logic": (2, 2), "loops": (1, 1)}
    assert body["recommendations"] == []


def test_wrong_quiz_answer_gets_feedback_and_recommendations(client, make_user, seed_all):
    user = make_user("a@example.com")
    response = _quiz(client, user["headers"], {"q1": 0, "q2": 0})
    assert response.status_code == 201
    body = response.json()
    assert body["score"] == 50 and body["passed"] is False
    first = body["feedback"][0]
    assert first["correct"] is False and first["correct_index"] == 1 and first["message"] == "Four."
    kinds = {r["type"] for r in body["recommendations"]}
    assert kinds == {"lesson", "resource"}
    assert all(r["concept_slug"] == "logic" for r in body["recommendations"])
    assert any(r["url"] == "https://example.com/logic" for r in body["recommendations"])
    lesson_slugs = {r["lesson_slug"] for r in body["recommendations"] if r["type"] == "lesson"}
    assert lesson_slugs == {"one", "two"}


@pytest.mark.parametrize("answers", [{"q1": 1}, {"q1": 1, "q2": 9}, {"q1": "1", "q2": 0}, {}])
def test_invalid_quiz_answers_are_422(client, make_user, seed_all, answers):
    user = make_user("a@example.com")
    response = _quiz(client, user["headers"], answers)
    assert response.status_code == 422 and response.json()["error"]["code"] == "invalid_answer"


def test_unknown_fields_in_submission_are_rejected(client, make_user, seed_all):
    user = make_user("a@example.com")
    exercise = _exercises(client, user["headers"])["quiz-one"]
    response = client.post(
        f"{API}/exercises/{exercise['id']}/submissions", json={"answer": {}, "score": 100}, headers=user["headers"]
    )
    assert response.status_code == 422


def test_code_submission_is_scored_from_reported_tests(client, make_user, seed_all):
    user = make_user("a@example.com")
    exercise = _exercises(client, user["headers"])["code-one"]
    url = f"{API}/exercises/{exercise['id']}/submissions"
    answer = {"code": "def double(n):\n    return n * 2\n", "results": [{"id": "t1", "passed": True}, {"id": "t2", "passed": False}]}
    body = client.post(url, json={"answer": answer}, headers=user["headers"]).json()
    assert body["score"] == 50 and body["passed"] is False

    bad = {"code": "x", "results": [{"id": "t1", "passed": True}]}
    assert client.post(url, json={"answer": bad}, headers=user["headers"]).status_code == 422
    empty = {"code": "  ", "results": [{"id": "t1", "passed": True}, {"id": "t2", "passed": True}]}
    assert client.post(url, json={"answer": empty}, headers=user["headers"]).status_code == 422


def test_puzzle_grading(client, make_user, seed_all):
    user = make_user("a@example.com")
    exercise = _exercises(client, user["headers"])["puzzle-one"]
    url = f"{API}/exercises/{exercise['id']}/submissions"
    solved = client.post(url, json={"answer": {"order": ["i0", "i1", "i2"]}}, headers=user["headers"]).json()
    assert solved["score"] == 100 and solved["passed"] is True
    reversed_ = client.post(url, json={"answer": {"order": ["i2", "i1", "i0"]}}, headers=user["headers"]).json()
    assert reversed_["score"] == 33
    bad = client.post(url, json={"answer": {"order": ["i0", "i1"]}}, headers=user["headers"])
    assert bad.status_code == 422


def test_attempts_best_score_and_history(client, make_user, seed_all):
    user = make_user("a@example.com")
    first = _quiz(client, user["headers"], {"q1": 0, "q2": 0}).json()
    second = _quiz(client, user["headers"], {"q1": 1, "q2": 0}).json()
    assert (first["attempt_number"], second["attempt_number"]) == (1, 2)
    exercise = _exercises(client, user["headers"])["quiz-one"]
    assert exercise["attempts"] == 2 and exercise["best_score"] == 100 and exercise["passed"] is True
    history = client.get(f"{API}/exercises/{exercise['id']}/submissions", headers=user["headers"]).json()
    assert [item["score"] for item in history] == [100, 50]


def test_submissions_are_private(client, make_user, seed_all):
    alice = make_user("alice@example.com")
    bob = make_user("bob@example.com")
    _quiz(client, alice["headers"], {"q1": 1, "q2": 0})
    exercise = _exercises(client, bob["headers"])["quiz-one"]
    assert exercise["attempts"] == 0
    assert client.get(f"{API}/exercises/{exercise['id']}/submissions", headers=bob["headers"]).json() == []
    assert client.get(f"{API}/assessments/mastery", headers=bob["headers"]).json() == []


def test_mastery_uses_only_the_latest_attempt(client, make_user, seed_all):
    user = make_user("a@example.com")
    _quiz(client, user["headers"], {"q1": 0, "q2": 0})
    _quiz(client, user["headers"], {"q1": 1, "q2": 0})
    mastery = {m["slug"]: (m["correct"], m["total"]) for m in client.get(f"{API}/assessments/mastery", headers=user["headers"]).json()}
    assert mastery == {"logic": (2, 2), "loops": (1, 1)}


def test_seed_is_idempotent(seed_all, curriculum_root, db_engine):
    assert seed_all.created == {"exercises": 3, "resources": 1}
    data = load_curriculum(curriculum_root)
    bundle = load_exercises(curriculum_root, data)
    with Session(db_engine) as session:
        again = seed_exercises(session, bundle)
        session.commit()
        assert again.created == {"exercises": 0, "resources": 0}
        assert again.updated == {"exercises": 0, "resources": 0}
        assert again.orphans == []
        assert session.scalar(select(func.count()).select_from(Exercise)) == 3
        assert session.scalar(select(func.count()).select_from(Resource)) == 1


def _load(root: Path):
    return load_exercises(root, load_curriculum(root))


def _mutated(exercises, index, **changes):
    copy = json.loads(json.dumps(exercises))
    copy[index].update(changes)
    return copy


def test_loader_accepts_the_sample(curriculum_root):
    write_exercises(curriculum_root)
    bundle = _load(curriculum_root)
    assert [e.slug for e in bundle.exercises] == ["quiz-one", "code-one", "puzzle-one"]
    assert len(bundle.resources) == 1


def test_loader_rejects_answer_out_of_range(curriculum_root):
    broken = json.loads(json.dumps(SAMPLE_EXERCISES))
    broken[0]["questions"][0]["answer"] = 7
    write_exercises(curriculum_root, broken)
    with pytest.raises(CurriculumError, match="answer"):
        _load(curriculum_root)


def test_loader_rejects_unknown_concept(curriculum_root):
    write_exercises(curriculum_root, _mutated(SAMPLE_EXERCISES, 0, concepts=["nope"]))
    with pytest.raises(CurriculumError, match="unknown concept"):
        _load(curriculum_root)


def test_loader_rejects_question_concept_outside_exercise(curriculum_root):
    broken = json.loads(json.dumps(SAMPLE_EXERCISES))
    broken[0]["questions"][0]["concept"] = "prompting"
    write_exercises(curriculum_root, broken)
    with pytest.raises(CurriculumError, match="not one of this exercise"):
        _load(curriculum_root)


def test_loader_rejects_exercises_for_a_planned_lesson(curriculum_root):
    write_exercises(curriculum_root, lesson="three")
    with pytest.raises(CurriculumError, match="planned"):
        _load(curriculum_root)


def test_loader_rejects_exercises_for_an_unknown_lesson(curriculum_root):
    write_exercises(curriculum_root, lesson="ghost")
    with pytest.raises(CurriculumError, match="no lesson"):
        _load(curriculum_root)


def test_loader_rejects_duplicate_puzzle_lines(curriculum_root):
    write_exercises(curriculum_root, _mutated(SAMPLE_EXERCISES, 2, lines=["a", "a"]))
    with pytest.raises(CurriculumError, match="different"):
        _load(curriculum_root)


def test_loader_rejects_insecure_resource_url(curriculum_root):
    bad = [{**SAMPLE_RESOURCES[0], "url": "http://example.com/x"}]
    write_exercises(curriculum_root, resources=bad)
    with pytest.raises(CurriculumError, match="https"):
        _load(curriculum_root)


def test_loader_rejects_bad_test_type(curriculum_root):
    broken = json.loads(json.dumps(SAMPLE_EXERCISES))
    broken[1]["tests"][0]["type"] = "magic"
    write_exercises(curriculum_root, broken)
    with pytest.raises(CurriculumError, match="return"):
        _load(curriculum_root)
