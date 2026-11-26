import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    Concept,
    Course,
    Exercise,
    ExerciseConcept,
    Lesson,
    LessonConcept,
    Module,
    Resource,
    Submission,
    SubmissionConceptResult,
)


def list_for_lesson(session: Session, lesson_id: uuid.UUID) -> list[Exercise]:
    return list(
        session.scalars(select(Exercise).where(Exercise.lesson_id == lesson_id).order_by(Exercise.position, Exercise.slug))
    )


def get(session: Session, exercise_id: uuid.UUID) -> Exercise | None:
    return session.get(Exercise, exercise_id)


def concepts_for(session: Session, exercise_id: uuid.UUID) -> list[Concept]:
    return list(
        session.scalars(
            select(Concept)
            .join(ExerciseConcept, ExerciseConcept.concept_id == Concept.id)
            .where(ExerciseConcept.exercise_id == exercise_id)
            .order_by(Concept.category, Concept.name)
        )
    )


def concepts_for_many(session: Session, exercise_ids: list[uuid.UUID]) -> dict[uuid.UUID, list[Concept]]:
    rows = session.execute(
        select(ExerciseConcept.exercise_id, Concept)
        .join(Concept, Concept.id == ExerciseConcept.concept_id)
        .where(ExerciseConcept.exercise_id.in_(exercise_ids))
        .order_by(Concept.category, Concept.name)
    ).all()
    result: dict[uuid.UUID, list[Concept]] = {}
    for exercise_id, concept in rows:
        result.setdefault(exercise_id, []).append(concept)
    return result


def attempt_stats(
    session: Session, user_id: uuid.UUID, exercise_ids: list[uuid.UUID]
) -> dict[uuid.UUID, tuple[int, int | None, bool]]:
    rows = session.execute(
        select(
            Submission.exercise_id,
            func.count(Submission.id),
            func.max(Submission.score),
            func.bool_or(Submission.passed),
        )
        .where(Submission.user_id == user_id, Submission.exercise_id.in_(exercise_ids))
        .group_by(Submission.exercise_id)
    ).all()
    return {exercise_id: (count, best, bool(passed)) for exercise_id, count, best, passed in rows}


def add_submission(session: Session, submission: Submission) -> Submission:
    session.add(submission)
    session.flush()
    return submission


def count_attempts(session: Session, user_id: uuid.UUID, exercise_id: uuid.UUID) -> int:
    return int(
        session.scalar(
            select(func.count(Submission.id)).where(Submission.user_id == user_id, Submission.exercise_id == exercise_id)
        )
        or 0
    )


def list_submissions(session: Session, user_id: uuid.UUID, exercise_id: uuid.UUID, limit: int = 20) -> list[Submission]:
    return list(
        session.scalars(
            select(Submission)
            .where(Submission.user_id == user_id, Submission.exercise_id == exercise_id)
            .order_by(Submission.created_at.desc(), Submission.id)
            .limit(limit)
        )
    )


def mastery(session: Session, user_id: uuid.UUID):
    """Per-concept totals using only each exercise's latest attempt, so retries cannot inflate the numbers."""
    ranked = (
        select(
            Submission.id.label("submission_id"),
            func.row_number()
            .over(
                partition_by=Submission.exercise_id,
                order_by=(Submission.created_at.desc(), Submission.id.desc()),
            )
            .label("rank"),
        )
        .where(Submission.user_id == user_id)
        .subquery()
    )
    latest = select(ranked.c.submission_id).where(ranked.c.rank == 1)
    return session.execute(
        select(
            Concept.slug,
            Concept.name,
            Concept.category,
            func.sum(SubmissionConceptResult.correct),
            func.sum(SubmissionConceptResult.total),
        )
        .select_from(SubmissionConceptResult)
        .join(Concept, Concept.id == SubmissionConceptResult.concept_id)
        .where(SubmissionConceptResult.submission_id.in_(latest))
        .group_by(Concept.slug, Concept.name, Concept.category)
        .order_by(Concept.category, Concept.name)
    ).all()


def lessons_for_concepts(session: Session, concept_ids: list[uuid.UUID]):
    return session.execute(
        select(LessonConcept.concept_id, Course.slug, Module.slug, Lesson.slug, Lesson.title)
        .select_from(LessonConcept)
        .join(Lesson, Lesson.id == LessonConcept.lesson_id)
        .join(Module, Module.id == Lesson.module_id)
        .join(Course, Course.id == Module.course_id)
        .where(LessonConcept.concept_id.in_(concept_ids), Lesson.status == "published")
        .order_by(Course.position, Module.position, Lesson.position)
    ).all()


def resources_for_concepts(session: Session, concept_ids: list[uuid.UUID]) -> list[Resource]:
    return list(
        session.scalars(
            select(Resource)
            .where(Resource.concept_id.in_(concept_ids))
            .order_by(Resource.is_open_source.desc(), Resource.title)
        )
    )
