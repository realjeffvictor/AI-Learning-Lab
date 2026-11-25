import json
from pathlib import Path

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Concept, Lesson, LessonConcept
from app.services.curriculum_loader import CurriculumError, load_curriculum

ZERO = {"concepts": 0, "courses": 0, "modules": 0, "lessons": 0}


def _edit_course(root: Path, edit) -> None:
    path = root / "courses" / "01-alpha" / "course.json"
    data = json.loads(path.read_text())
    edit(data)
    path.write_text(json.dumps(data))


def test_loader_reads_sample(curriculum_root):
    data = load_curriculum(curriculum_root)
    assert [c.slug for c in data.courses] == ["alpha", "beta"]
    assert len(data.concepts) == 3
    lessons = data.courses[0].modules[0].lessons
    assert [lesson.content_md is not None for lesson in lessons] == [True, True, False]


def test_seed_creates_everything(seed, db_engine):
    report = seed()
    assert report.created == {"concepts": 3, "courses": 2, "modules": 2, "lessons": 3}
    with Session(db_engine) as session:
        statuses = {lesson.slug: lesson.status for lesson in session.scalars(select(Lesson))}
        assert statuses == {"one": "published", "two": "published", "three": "planned"}
        assert session.scalar(select(func.count()).select_from(LessonConcept)) == 3


def test_seed_is_idempotent(seed):
    seed()
    second = seed()
    assert second.created == ZERO
    assert second.updated == ZERO
    assert second.orphans == []


def test_seed_updates_changed_fields_without_duplicating(seed, curriculum_root):
    seed()
    _edit_course(curriculum_root, lambda d: d.update(title="Alpha Renamed"))
    report = seed()
    assert report.created == ZERO
    assert report.updated["courses"] == 1


def test_seed_syncs_lesson_concepts(seed, curriculum_root, db_engine):
    seed()
    _edit_course(curriculum_root, lambda d: d["modules"][0]["lessons"][0].update(concepts=["prompting"]))
    report = seed()
    assert report.updated["lessons"] == 1
    with Session(db_engine) as session:
        slugs = set(
            session.scalars(
                select(Concept.slug)
                .join(LessonConcept, LessonConcept.concept_id == Concept.id)
                .join(Lesson, Lesson.id == LessonConcept.lesson_id)
                .where(Lesson.slug == "one")
            )
        )
    assert slugs == {"prompting"}


def test_missing_content_is_reported_as_orphan_not_deleted(seed, curriculum_root, db_engine):
    seed()
    _edit_course(curriculum_root, lambda d: d["modules"][0]["lessons"].pop())
    report = seed()
    assert any("three" in orphan for orphan in report.orphans)
    with Session(db_engine) as session:
        assert session.scalar(select(func.count()).select_from(Lesson)) == 3


def test_loader_rejects_unknown_concept(curriculum_root):
    _edit_course(curriculum_root, lambda d: d["modules"][0]["lessons"][0].update(concepts=["nope"]))
    with pytest.raises(CurriculumError, match="nope"):
        load_curriculum(curriculum_root)


def test_loader_rejects_bad_slug(curriculum_root):
    _edit_course(curriculum_root, lambda d: d["modules"][0]["lessons"][0].update(slug="Bad Slug"))
    with pytest.raises(CurriculumError, match="invalid slug"):
        load_curriculum(curriculum_root)


def test_loader_rejects_duplicate_lesson_slugs(curriculum_root):
    _edit_course(curriculum_root, lambda d: d["modules"][0]["lessons"][1].update(slug="one"))
    with pytest.raises(CurriculumError, match="duplicate lesson slug"):
        load_curriculum(curriculum_root)


def test_loader_rejects_stage_without_number(curriculum_root):
    _edit_course(curriculum_root, lambda d: d.pop("stage_number"))
    with pytest.raises(CurriculumError, match="stage_number"):
        load_curriculum(curriculum_root)


def test_loader_rejects_empty_markdown(curriculum_root):
    (curriculum_root / "courses" / "01-alpha" / "intro" / "one.md").write_text("   \n")
    with pytest.raises(CurriculumError, match="empty"):
        load_curriculum(curriculum_root)


def test_loader_rejects_unlisted_markdown(curriculum_root):
    (curriculum_root / "courses" / "01-alpha" / "intro" / "stray.md").write_text("Not listed anywhere.")
    with pytest.raises(CurriculumError, match="not listed"):
        load_curriculum(curriculum_root)
