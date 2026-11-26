"""Writes validated exercises and resources into the database. Safe to run repeatedly; never deletes."""
import uuid
from dataclasses import dataclass, field

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models import Concept, Course, Exercise, ExerciseConcept, Lesson, Module, Resource
from app.services.curriculum_loader import CurriculumError
from app.services.curriculum_seed import _apply
from app.services.exercise_loader import ExerciseBundle


def _zero() -> dict[str, int]:
    return {"exercises": 0, "resources": 0}


@dataclass
class ExerciseSeedReport:
    created: dict[str, int] = field(default_factory=_zero)
    updated: dict[str, int] = field(default_factory=_zero)
    orphans: list[str] = field(default_factory=list)


def seed_exercises(session: Session, bundle: ExerciseBundle) -> ExerciseSeedReport:
    report = ExerciseSeedReport()
    concepts = {c.slug: c for c in session.scalars(select(Concept))}
    lesson_ids = {
        (course_slug, module_slug, lesson_slug): lesson_id
        for course_slug, module_slug, lesson_slug, lesson_id in session.execute(
            select(Course.slug, Module.slug, Lesson.slug, Lesson.id)
            .select_from(Lesson)
            .join(Module, Module.id == Lesson.module_id)
            .join(Course, Course.id == Module.course_id)
        ).all()
    }

    positions: dict[uuid.UUID, int] = {}
    wanted: set[tuple[uuid.UUID, str]] = set()
    for item in bundle.exercises:
        lesson_id = lesson_ids.get((item.course_slug, item.module_slug, item.lesson_slug))
        if lesson_id is None:
            raise CurriculumError(
                f"{item.course_slug}/{item.module_slug}/{item.lesson_slug}: lesson is not in the database; seed the curriculum first"
            )
        positions[lesson_id] = positions.get(lesson_id, 0) + 1
        values = {
            "title": item.title,
            "kind": item.kind,
            "position": positions[lesson_id],
            "instructions_md": item.instructions,
            "definition": item.definition,
            "pass_score": item.pass_score,
        }
        existing = session.scalar(select(Exercise).where(Exercise.lesson_id == lesson_id, Exercise.slug == item.slug))
        if existing is not None and existing.managed_in_app:
            wanted.add((lesson_id, item.slug))
            report.orphans.append(f"exercise {item.slug} (edited in the app; the file was not applied)")
            continue
        changed = False
        if existing is None:
            exercise = Exercise(lesson_id=lesson_id, slug=item.slug, **values)
            session.add(exercise)
            report.created["exercises"] += 1
        else:
            exercise = existing
            changed = _apply(exercise, values)
        session.flush()
        wanted.add((lesson_id, item.slug))

        wanted_concepts = {concepts[slug].id for slug in item.concepts}
        current = set(
            session.scalars(select(ExerciseConcept.concept_id).where(ExerciseConcept.exercise_id == exercise.id))
        )
        for concept_id in wanted_concepts - current:
            session.add(ExerciseConcept(exercise_id=exercise.id, concept_id=concept_id))
            changed = changed or existing is not None
        stale = current - wanted_concepts
        if stale:
            session.execute(
                delete(ExerciseConcept).where(
                    ExerciseConcept.exercise_id == exercise.id, ExerciseConcept.concept_id.in_(stale)
                )
            )
            changed = True
        if changed and existing is not None:
            report.updated["exercises"] += 1

    existing_resources = {r.url: r for r in session.scalars(select(Resource))}
    for resource in bundle.resources:
        values = {
            "title": resource.title,
            "kind": resource.kind,
            "concept_id": concepts[resource.concept].id,
            "level": resource.level,
            "is_open_source": resource.is_open_source,
        }
        current_row = existing_resources.get(resource.url)
        if current_row is None:
            session.add(Resource(url=resource.url, **values))
            report.created["resources"] += 1
        elif _apply(current_row, values):
            report.updated["resources"] += 1
    session.flush()

    for lesson_id, slug in session.execute(select(Exercise.lesson_id, Exercise.slug)).all():
        if (lesson_id, slug) not in wanted:
            report.orphans.append(f"exercise {slug} (lesson {lesson_id})")
    wanted_urls = {r.url for r in bundle.resources}
    for url in existing_resources:
        if url not in wanted_urls:
            report.orphans.append(f"resource {url}")
    return report
