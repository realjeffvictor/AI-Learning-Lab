"""Checks the real files in curriculum/, not test fixtures. Runs in CI so a bad lesson or exercise cannot be merged."""
from pathlib import Path

import pytest

from app.services.curriculum_loader import load_curriculum
from app.services.exercise_loader import load_exercises
from app.services.project_loader import load_projects

ROOT = Path(__file__).resolve().parents[2] / "curriculum"


@pytest.fixture(scope="module")
def data():
    return load_curriculum(ROOT)


def test_every_curriculum_file_is_valid(data):
    load_exercises(ROOT, data)
    load_projects(ROOT, data)


def test_every_written_lesson_has_a_quiz(data):
    bundle = load_exercises(ROOT, data)
    with_quiz = {(e.course_slug, e.module_slug, e.lesson_slug) for e in bundle.exercises if e.kind == "quiz"}
    missing = [
        f"{course.slug}/{module.slug}/{lesson.slug}"
        for course in data.courses
        for module in course.modules
        for lesson in module.lessons
        if lesson.content_md and (course.slug, module.slug, lesson.slug) not in with_quiz
    ]
    assert not missing, f"written lessons without a quiz: {missing}"


def test_stage_one_has_the_expected_written_lessons(data):
    stage = next(c for c in data.courses if c.slug == "python-fundamentals")
    written = [lesson.slug for module in stage.modules for lesson in module.lessons if lesson.content_md]
    assert len(written) >= 10 and len(set(written)) == len(written)
