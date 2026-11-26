import json
from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.curriculum_loader import CurriculumError, load_curriculum
from app.services.project_loader import load_projects
from app.services.project_seed import seed_projects

API = "/api/v1"
COURSES = "/api/v1/courses"
LONG_DOC = "d" * 700
REFLECTION = "r" * 120
REPO = "https://github.com/alice/build-it"
RUBRIC = {"understanding": 3, "implementation": 3, "verification": 3, "ownership": 3}

BUILD_META = {
    "title": "Build it", "summary": "Build something.", "kind": "build", "concepts": ["logic"],
    "requirements": [{"id": "r1", "text": "Does a thing"}, {"id": "r2", "text": "Handles errors"}],
}
DESIGN_META = {
    "title": "Design it", "summary": "Design something.", "kind": "architecture", "concepts": ["logic", "loops"],
    "requirements": [{"id": "r1", "text": "States the context"}],
}
SAMPLE = {"build-it": (BUILD_META, "# Build it\n\nBrief text."), "design-it": (DESIGN_META, "# Design it\n\nOther brief.")}


def write_projects(root: Path, projects=None, course: str = "alpha") -> None:
    folder = root / "projects" / course
    folder.mkdir(parents=True, exist_ok=True)
    for slug, (meta, brief) in (SAMPLE if projects is None else projects).items():
        (folder / f"{slug}.json").write_text(json.dumps(meta))
        (folder / f"{slug}.md").write_text(brief)


@pytest.fixture
def projects_seeded(curriculum_root, db_engine, seed):
    write_projects(curriculum_root)
    seed()
    data = load_curriculum(curriculum_root)
    with Session(db_engine) as session:
        report = seed_projects(session, load_projects(curriculum_root, data))
        session.commit()
    return report


def _project_id(client, headers, slug="build-it") -> str:
    listing = client.get(f"{API}/projects", headers=headers).json()
    return {item["slug"]: item["id"] for item in listing}[slug]


def _save(client, headers, project_id, **fields):
    return client.put(f"{API}/projects/{project_id}/submission", json=fields, headers=headers)


def _fill(client, headers, slug="build-it") -> str:
    project_id = _project_id(client, headers, slug)
    fields = {"documentation_md": LONG_DOC, "reflection_md": REFLECTION}
    if slug == "build-it":
        fields.update(repo_url=REPO, requirement_checks={"r1": True, "r2": True})
    else:
        fields["requirement_checks"] = {"r1": True}
    assert _save(client, headers, project_id, **fields).status_code == 200
    return project_id


def _submit(client, headers, slug="build-it") -> str:
    project_id = _fill(client, headers, slug)
    response = client.post(f"{API}/projects/{project_id}/submission/submit", headers=headers)
    assert response.status_code == 200, response.text
    return project_id


def _submission_id(client, headers, slug="build-it") -> str:
    return client.get(f"{API}/projects/alpha/{slug}", headers=headers).json()["submission"]["id"]


def _review(client, headers, submission_id, outcome="approved", rubric=None, feedback="Good work, clear and complete."):
    body = {"outcome": outcome, "rubric_scores": rubric or RUBRIC, "feedback": feedback}
    return client.post(f"{API}/reviews/submissions/{submission_id}", json=body, headers=headers)


# ------------------------------------------------------------------ learner side
def test_projects_require_authentication(client):
    assert client.get(f"{API}/projects").status_code == 401
    assert client.get(f"{API}/achievements").status_code == 401


def test_list_projects(client, make_user, projects_seeded):
    user = make_user("a@example.com")
    listing = client.get(f"{API}/projects", headers=user["headers"]).json()
    assert [(p["slug"], p["kind"], p["requirements_count"]) for p in listing] == [
        ("build-it", "build", 2), ("design-it", "architecture", 1)
    ]
    assert all(p["status"] == "not_started" and p["course_slug"] == "alpha" for p in listing)


def test_project_detail(client, make_user, projects_seeded):
    user = make_user("a@example.com")
    body = client.get(f"{API}/projects/alpha/build-it", headers=user["headers"]).json()
    assert body["brief_md"].startswith("# Build it")
    assert [r["id"] for r in body["requirements"]] == ["r1", "r2"]
    assert body["requires_repo"] is True and body["submission"] is None and body["reviews"] == []
    assert (body["min_documentation_chars"], body["min_reflection_chars"]) == (200, 100)
    assert [c["slug"] for c in body["concepts"]] == ["logic"]
    design = client.get(f"{API}/projects/alpha/design-it", headers=user["headers"]).json()
    assert design["requires_repo"] is False and design["min_documentation_chars"] == 600


def test_unknown_project_is_404(client, make_user, projects_seeded):
    user = make_user("a@example.com")
    response = client.get(f"{API}/projects/alpha/nope", headers=user["headers"])
    assert response.status_code == 404 and response.json()["error"]["code"] == "project_not_found"
    missing = "00000000-0000-4000-8000-000000000000"
    assert _save(client, user["headers"], missing).status_code == 404
    assert client.post(f"{API}/projects/{missing}/submission/submit", headers=user["headers"]).status_code == 404


def test_saving_a_draft_creates_and_updates_it(client, make_user, projects_seeded):
    user = make_user("a@example.com")
    project_id = _project_id(client, user["headers"])
    first = _save(client, user["headers"], project_id, documentation_md="Hello")
    assert first.status_code == 200 and first.json()["status"] == "draft"
    second = _save(client, user["headers"], project_id, reflection_md="Thoughts").json()
    assert second["documentation_md"] == "Hello" and second["reflection_md"] == "Thoughts"
    detail = client.get(f"{API}/projects/alpha/build-it", headers=user["headers"]).json()
    assert detail["submission"]["documentation_md"] == "Hello"
    listing = client.get(f"{API}/projects", headers=user["headers"]).json()
    assert {p["slug"]: p["status"] for p in listing}["build-it"] == "draft"


def test_repo_url_is_normalised_and_can_be_cleared(client, make_user, projects_seeded):
    user = make_user("a@example.com")
    project_id = _project_id(client, user["headers"])
    saved = _save(client, user["headers"], project_id, repo_url=" https://github.com/alice/build-it.git/ ").json()
    assert saved["repo_url"] == REPO
    assert _save(client, user["headers"], project_id, repo_url="").json()["repo_url"] is None


@pytest.mark.parametrize(
    "fields",
    [
        {"repo_url": "https://evil.example/alice/x"},
        {"repo_url": "http://github.com/alice/x"},
        {"repo_url": "https://github.com/alice/x/tree/main"},
        {"repo_url": "https://github.com/../x"},
        {"requirement_checks": {"r1": "maybe"}},
        {"documentation_md": "x" * 20001},
        {"role": "admin"},
    ],
)
def test_draft_input_is_validated(client, make_user, projects_seeded, fields):
    user = make_user("a@example.com")
    assert _save(client, user["headers"], _project_id(client, user["headers"]), **fields).status_code == 422


def test_unknown_requirement_and_repo_on_non_build_project_are_rejected(client, make_user, projects_seeded):
    user = make_user("a@example.com")
    build = _project_id(client, user["headers"])
    response = _save(client, user["headers"], build, requirement_checks={"nope": True})
    assert response.status_code == 422 and response.json()["error"]["code"] == "invalid_requirement"
    design = _project_id(client, user["headers"], "design-it")
    response = _save(client, user["headers"], design, repo_url=REPO)
    assert response.status_code == 422 and response.json()["error"]["code"] == "repo_not_applicable"


def test_submit_needs_a_draft_and_a_complete_one(client, make_user, projects_seeded):
    user = make_user("a@example.com")
    headers = user["headers"]
    project_id = _project_id(client, headers)
    url = f"{API}/projects/{project_id}/submission/submit"
    no_draft = client.post(url, headers=headers)
    assert no_draft.status_code == 409 and no_draft.json()["error"]["code"] == "no_draft"

    assert _save(client, headers, project_id).status_code == 200
    incomplete = client.post(url, headers=headers)
    assert incomplete.status_code == 422 and incomplete.json()["error"]["code"] == "submission_incomplete"
    message = incomplete.json()["error"]["message"]
    for expected in ("repository", "requirement", "Documentation", "Reflection"):
        assert expected in message


def test_submit_succeeds_then_locks_editing(client, make_user, projects_seeded):
    user = make_user("a@example.com")
    headers = user["headers"]
    project_id = _submit(client, headers)
    detail = client.get(f"{API}/projects/alpha/build-it", headers=headers).json()
    assert detail["submission"]["status"] == "submitted" and detail["submission"]["submitted_at"] is not None
    locked = _save(client, headers, project_id, documentation_md="changed")
    assert locked.status_code == 409 and locked.json()["error"]["code"] == "submission_locked"
    again = client.post(f"{API}/projects/{project_id}/submission/submit", headers=headers)
    assert again.status_code == 409


def test_architecture_project_needs_no_repository(client, make_user, projects_seeded):
    user = make_user("a@example.com")
    _submit(client, user["headers"], "design-it")


def test_submissions_are_private(client, make_user, projects_seeded):
    alice = make_user("alice@example.com")
    bob = make_user("bob@example.com")
    _fill(client, alice["headers"])
    detail = client.get(f"{API}/projects/alpha/build-it", headers=bob["headers"]).json()
    assert detail["submission"] is None
    listing = client.get(f"{API}/projects", headers=bob["headers"]).json()
    assert {p["slug"]: p["status"] for p in listing}["build-it"] == "not_started"


# ------------------------------------------------------------------ reviewer side
def test_review_endpoints_are_staff_only(client, make_user, projects_seeded):
    student = make_user("student@example.com")
    assert client.get(f"{API}/reviews/queue").status_code == 401
    assert client.get(f"{API}/reviews/queue", headers=student["headers"]).status_code == 403
    missing = "00000000-0000-4000-8000-000000000000"
    assert client.get(f"{API}/reviews/submissions/{missing}", headers=student["headers"]).status_code == 403
    assert _review(client, student["headers"], missing).status_code == 403


@pytest.mark.parametrize("role", ["instructor", "admin"])
def test_queue_lists_submitted_work_only(client, make_user, projects_seeded, role):
    alice = make_user("alice@example.com")
    staff = make_user(f"{role}@example.com", role)
    _fill(client, alice["headers"], "design-it")  # a draft: must not appear
    _submit(client, alice["headers"], "build-it")
    body = client.get(f"{API}/reviews/queue", headers=staff["headers"]).json()
    assert body["total"] == 1 and len(body["items"]) == 1
    item = body["items"][0]
    assert item["learner_email"] == "alice@example.com" and item["project_title"] == "Build it"
    assert item["project_kind"] == "build" and item["course_slug"] == "alpha"


def test_reviewers_cannot_see_drafts(client, make_user, projects_seeded):
    alice = make_user("alice@example.com")
    teacher = make_user("teacher@example.com", "instructor")
    _fill(client, alice["headers"])
    draft_id = _submission_id(client, alice["headers"])
    assert client.get(f"{API}/reviews/submissions/{draft_id}", headers=teacher["headers"]).status_code == 404
    response = _review(client, teacher["headers"], draft_id)
    assert response.status_code == 409 and response.json()["error"]["code"] == "not_awaiting_review"


def test_review_detail_includes_everything_a_reviewer_needs(client, make_user, projects_seeded):
    alice = make_user("alice@example.com")
    teacher = make_user("teacher@example.com", "instructor")
    _submit(client, alice["headers"])
    submission_id = _submission_id(client, alice["headers"])
    body = client.get(f"{API}/reviews/submissions/{submission_id}", headers=teacher["headers"]).json()
    assert body["learner_name"] == "alice" and body["brief_md"].startswith("# Build it")
    assert body["submission"]["repo_url"] == REPO and body["submission"]["documentation_md"] == LONG_DOC
    assert [r["id"] for r in body["requirements"]] == ["r1", "r2"] and body["reviews"] == []


def test_approving_a_submission(client, make_user, projects_seeded, db_engine):
    alice = make_user("alice@example.com")
    teacher = make_user("teacher@example.com", "instructor")
    _submit(client, alice["headers"])
    submission_id = _submission_id(client, alice["headers"])
    response = _review(client, teacher["headers"], submission_id)
    assert response.status_code == 200
    assert response.json()["submission"]["status"] == "approved"
    detail = client.get(f"{API}/projects/alpha/build-it", headers=alice["headers"]).json()
    review = detail["reviews"][0]
    assert review["outcome"] == "approved" and review["rubric_scores"] == RUBRIC
    assert review["reviewer_name"] == "teacher" and review["feedback"] == "Good work, clear and complete."
    assert client.get(f"{API}/reviews/queue", headers=teacher["headers"]).json()["total"] == 0
    with db_engine.connect() as connection:
        count = connection.scalar(text("SELECT count(*) FROM audit_logs WHERE action = 'project.reviewed'"))
    assert count == 1


@pytest.mark.parametrize(
    "rubric",
    [
        {"understanding": 3, "implementation": 3, "verification": 3},
        {**RUBRIC, "ownership": 5},
        {**RUBRIC, "ownership": 0},
        {**RUBRIC, "style": 3},
    ],
)
def test_rubric_is_validated(client, make_user, projects_seeded, rubric):
    alice = make_user("alice@example.com")
    teacher = make_user("teacher@example.com", "instructor")
    _submit(client, alice["headers"])
    submission_id = _submission_id(client, alice["headers"])
    assert _review(client, teacher["headers"], submission_id, rubric=rubric).status_code == 422


def test_approval_needs_a_minimum_score_and_feedback(client, make_user, projects_seeded):
    alice = make_user("alice@example.com")
    teacher = make_user("teacher@example.com", "instructor")
    _submit(client, alice["headers"])
    submission_id = _submission_id(client, alice["headers"])
    low = _review(client, teacher["headers"], submission_id, rubric={**RUBRIC, "verification": 1})
    assert low.status_code == 422 and low.json()["error"]["code"] == "rubric_too_low"
    assert _review(client, teacher["headers"], submission_id, feedback="short").status_code == 422
    still = client.get(f"{API}/projects/alpha/build-it", headers=alice["headers"]).json()
    assert still["submission"]["status"] == "submitted" and still["reviews"] == []


def test_reviewers_cannot_review_their_own_work(client, make_user, projects_seeded):
    teacher = make_user("teacher@example.com", "instructor")
    _submit(client, teacher["headers"])
    submission_id = _submission_id(client, teacher["headers"])
    response = _review(client, teacher["headers"], submission_id)
    assert response.status_code == 403 and response.json()["error"]["code"] == "cannot_review_own"


def test_unknown_submission_is_404(client, make_user, projects_seeded):
    teacher = make_user("teacher@example.com", "instructor")
    missing = "00000000-0000-4000-8000-000000000000"
    assert _review(client, teacher["headers"], missing).status_code == 404
    assert client.get(f"{API}/reviews/submissions/{missing}", headers=teacher["headers"]).status_code == 404


def test_changes_requested_then_resubmit_then_approve_keeps_history(client, make_user, projects_seeded):
    alice = make_user("alice@example.com")
    teacher = make_user("teacher@example.com", "instructor")
    project_id = _submit(client, alice["headers"])
    submission_id = _submission_id(client, alice["headers"])

    first = _review(
        client, teacher["headers"], submission_id, outcome="changes_requested",
        rubric={**RUBRIC, "verification": 1}, feedback="Please show how you tested this.",
    )
    assert first.status_code == 200 and first.json()["submission"]["status"] == "changes_requested"

    edited = _save(client, alice["headers"], project_id, documentation_md=LONG_DOC + " Added a testing section.")
    assert edited.status_code == 200 and edited.json()["status"] == "changes_requested"
    assert client.post(f"{API}/projects/{project_id}/submission/submit", headers=alice["headers"]).status_code == 200

    assert _review(client, teacher["headers"], submission_id).status_code == 200
    assert _review(client, teacher["headers"], submission_id).status_code == 409  # already approved
    detail = client.get(f"{API}/projects/alpha/build-it", headers=alice["headers"]).json()
    assert detail["submission"]["status"] == "approved"
    assert [r["outcome"] for r in detail["reviews"]] == ["approved", "changes_requested"]


# ------------------------------------------------------------------ achievements
def test_achievements_start_empty(client, make_user, projects_seeded):
    user = make_user("a@example.com")
    body = client.get(f"{API}/achievements", headers=user["headers"]).json()
    assert len(body) == 7 and not any(item["earned"] for item in body)
    assert {item["key"] for item in body} == {
        "first-lesson", "first-pass", "perfect-score", "first-project-submitted", "builder", "architect", "reviewer",
    }


def _earned(client, headers) -> dict:
    return {i["key"]: i["earned_at"] for i in client.get(f"{API}/achievements", headers=headers).json() if i["earned"]}


def test_project_achievements_follow_the_evidence(client, make_user, projects_seeded):
    alice = make_user("alice@example.com")
    teacher = make_user("teacher@example.com", "instructor")
    _submit(client, alice["headers"])
    assert set(_earned(client, alice["headers"])) == {"first-project-submitted"}

    _review(client, teacher["headers"], _submission_id(client, alice["headers"]))
    assert set(_earned(client, alice["headers"])) == {"first-project-submitted", "builder"}

    _submit(client, alice["headers"], "design-it")
    _review(client, teacher["headers"], _submission_id(client, alice["headers"], "design-it"))
    assert "architect" in _earned(client, alice["headers"])
    assert "reviewer" not in _earned(client, alice["headers"])


def test_changes_requested_does_not_earn_builder(client, make_user, projects_seeded):
    alice = make_user("alice@example.com")
    teacher = make_user("teacher@example.com", "instructor")
    _submit(client, alice["headers"])
    _review(client, teacher["headers"], _submission_id(client, alice["headers"]), outcome="changes_requested")
    assert set(_earned(client, alice["headers"])) == {"first-project-submitted"}


def test_achievements_are_stable_and_private(client, make_user, projects_seeded):
    alice = make_user("alice@example.com")
    bob = make_user("bob@example.com")
    course = client.get(f"{COURSES}/alpha", headers=alice["headers"]).json()
    lesson_id = {l["slug"]: l["id"] for m in course["modules"] for l in m["lessons"]}["one"]
    assert client.post(f"{API}/progress/lessons/{lesson_id}/complete", headers=alice["headers"]).status_code == 200
    first = _earned(client, alice["headers"])
    second = _earned(client, alice["headers"])
    assert list(first) == ["first-lesson"] and first == second
    assert _earned(client, bob["headers"]) == {}


# ------------------------------------------------------------------ loader and seed
def _load(root: Path):
    return load_projects(root, load_curriculum(root))


def test_loader_reads_the_sample(curriculum_root):
    write_projects(curriculum_root)
    projects = _load(curriculum_root)
    assert [(p.course_slug, p.slug, p.kind) for p in projects] == [
        ("alpha", "build-it", "build"), ("alpha", "design-it", "architecture")
    ]
    assert projects[0].requirements[0] == ("r1", "Does a thing") and projects[0].brief_md.startswith("# Build it")


def test_loader_returns_nothing_without_a_projects_folder(curriculum_root):
    assert _load(curriculum_root) == ()


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"concepts": ["nope"]}, "unknown concept"),
        ({"concepts": []}, "at least one concept"),
        ({"kind": "essay"}, "kind"),
        ({"requirements": []}, "requirements"),
        ({"requirements": [{"id": "a", "text": "x"}, {"id": "a", "text": "y"}]}, "duplicate requirement"),
        ({"requirements": [{"id": "Bad Id", "text": "x"}]}, "id"),
    ],
)
def test_loader_rejects_bad_project_files(curriculum_root, change, message):
    write_projects(curriculum_root, {"build-it": ({**BUILD_META, **change}, "# Brief")})
    with pytest.raises(CurriculumError, match=message):
        _load(curriculum_root)


def test_loader_rejects_missing_empty_and_orphan_briefs(curriculum_root):
    write_projects(curriculum_root)
    folder = curriculum_root / "projects" / "alpha"
    (folder / "design-it.md").unlink()
    with pytest.raises(CurriculumError, match="missing brief"):
        _load(curriculum_root)
    (folder / "design-it.md").write_text("   \n")
    with pytest.raises(CurriculumError, match="empty"):
        _load(curriculum_root)
    (folder / "design-it.md").write_text("ok")
    (folder / "stray.md").write_text("no json")
    with pytest.raises(CurriculumError, match="no matching .json"):
        _load(curriculum_root)


def test_loader_rejects_unknown_course_folder(curriculum_root):
    write_projects(curriculum_root, course="ghost")
    with pytest.raises(CurriculumError, match="no course"):
        _load(curriculum_root)


def test_seed_is_idempotent_and_syncs_concepts(projects_seeded, curriculum_root, db_engine):
    assert projects_seeded.created == {"projects": 2}
    write_projects(curriculum_root)
    data = load_curriculum(curriculum_root)
    with Session(db_engine) as session:
        again = seed_projects(session, load_projects(curriculum_root, data))
        session.commit()
        assert again.created == {"projects": 0} and again.updated == {"projects": 0} and again.orphans == []

    changed = {"build-it": ({**BUILD_META, "concepts": ["loops"]}, "# Build it\n\nBrief text."), "design-it": SAMPLE["design-it"]}
    write_projects(curriculum_root, changed)
    with Session(db_engine) as session:
        report = seed_projects(session, load_projects(curriculum_root, load_curriculum(curriculum_root)))
        session.commit()
    assert report.updated == {"projects": 1} and report.created == {"projects": 0}
