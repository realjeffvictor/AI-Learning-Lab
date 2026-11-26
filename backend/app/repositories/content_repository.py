import uuid

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session, selectinload

from app.models import Concept, Course, Exercise, ExerciseConcept, Lesson, LessonConcept, Module, Submission


def tree(session: Session) -> list[Course]:
    return list(
        session.scalars(
            select(Course)
            .order_by(Course.position, Course.slug)
            .options(selectinload(Course.modules).selectinload(Module.lessons))
        )
    )


def exercise_counts(session: Session) -> dict[uuid.UUID, int]:
    rows = session.execute(select(Exercise.lesson_id, func.count(Exercise.id)).group_by(Exercise.lesson_id)).all()
    return {lesson_id: int(count) for lesson_id, count in rows}


def all_concepts(session: Session) -> list[Concept]:
    return list(session.scalars(select(Concept).order_by(Concept.category, Concept.name)))


def concepts_by_slugs(session: Session, slugs: list[str]) -> dict[str, Concept]:
    if not slugs:
        return {}
    return {c.slug: c for c in session.scalars(select(Concept).where(Concept.slug.in_(slugs)))}


def lesson_concept_slugs(session: Session, lesson_id: uuid.UUID) -> list[str]:
    return list(
        session.scalars(
            select(Concept.slug)
            .join(LessonConcept, LessonConcept.concept_id == Concept.id)
            .where(LessonConcept.lesson_id == lesson_id)
            .order_by(Concept.category, Concept.name)
        )
    )


def replace_lesson_concepts(session: Session, lesson_id: uuid.UUID, concept_ids: list[uuid.UUID]) -> None:
    session.execute(delete(LessonConcept).where(LessonConcept.lesson_id == lesson_id))
    for concept_id in concept_ids:
        session.add(LessonConcept(lesson_id=lesson_id, concept_id=concept_id))


def next_lesson_position(session: Session, module_id: uuid.UUID) -> int:
    return int(session.scalar(select(func.coalesce(func.max(Lesson.position), 0)).where(Lesson.module_id == module_id)) or 0) + 1


def lesson_slug_taken(session: Session, module_id: uuid.UUID, slug: str) -> bool:
    return session.scalar(select(Lesson.id).where(Lesson.module_id == module_id, Lesson.slug == slug)) is not None


def exercise_slug_taken(session: Session, lesson_id: uuid.UUID, slug: str) -> bool:
    return session.scalar(select(Exercise.id).where(Exercise.lesson_id == lesson_id, Exercise.slug == slug)) is not None


def next_exercise_position(session: Session, lesson_id: uuid.UUID) -> int:
    return int(
        session.scalar(select(func.coalesce(func.max(Exercise.position), 0)).where(Exercise.lesson_id == lesson_id)) or 0
    ) + 1


def exercise_concept_slugs(session: Session, exercise_id: uuid.UUID) -> list[str]:
    return list(
        session.scalars(
            select(Concept.slug)
            .join(ExerciseConcept, ExerciseConcept.concept_id == Concept.id)
            .where(ExerciseConcept.exercise_id == exercise_id)
            .order_by(Concept.category, Concept.name)
        )
    )


def replace_exercise_concepts(session: Session, exercise_id: uuid.UUID, concept_ids: list[uuid.UUID]) -> None:
    session.execute(delete(ExerciseConcept).where(ExerciseConcept.exercise_id == exercise_id))
    for concept_id in concept_ids:
        session.add(ExerciseConcept(exercise_id=exercise_id, concept_id=concept_id))


def count_exercise_submissions(session: Session, exercise_id: uuid.UUID) -> int:
    return int(session.scalar(select(func.count(Submission.id)).where(Submission.exercise_id == exercise_id)) or 0)
