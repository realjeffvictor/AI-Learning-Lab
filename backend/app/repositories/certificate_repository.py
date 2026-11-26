import uuid

from sqlalchemy import distinct, select
from sqlalchemy.orm import Session

from app.models import (
    Certificate,
    Exercise,
    Lesson,
    LessonProgress,
    Module,
    Project,
    ProjectSubmission,
    Submission,
)


def published_lesson_ids(session: Session, course_id: uuid.UUID) -> set[uuid.UUID]:
    return set(
        session.scalars(
            select(Lesson.id)
            .join(Module, Module.id == Lesson.module_id)
            .where(Module.course_id == course_id, Lesson.status == "published")
        )
    )


def completed_among(session: Session, user_id: uuid.UUID, lesson_ids: set[uuid.UUID]) -> set[uuid.UUID]:
    if not lesson_ids:
        return set()
    return set(
        session.scalars(
            select(LessonProgress.lesson_id).where(
                LessonProgress.user_id == user_id,
                LessonProgress.status == "completed",
                LessonProgress.lesson_id.in_(lesson_ids),
            )
        )
    )


def server_graded_exercise_ids(session: Session, course_id: uuid.UUID) -> set[uuid.UUID]:
    """Quizzes and puzzles only. Code exercise scores are reported by the browser, so they never count toward a certificate."""
    return set(
        session.scalars(
            select(Exercise.id)
            .join(Lesson, Lesson.id == Exercise.lesson_id)
            .join(Module, Module.id == Lesson.module_id)
            .where(Module.course_id == course_id, Lesson.status == "published", Exercise.kind.in_(("quiz", "puzzle")))
        )
    )


def passed_among(session: Session, user_id: uuid.UUID, exercise_ids: set[uuid.UUID]) -> set[uuid.UUID]:
    if not exercise_ids:
        return set()
    return set(
        session.scalars(
            select(distinct(Submission.exercise_id)).where(
                Submission.user_id == user_id, Submission.passed.is_(True), Submission.exercise_id.in_(exercise_ids)
            )
        )
    )


def project_ids(session: Session, course_id: uuid.UUID) -> set[uuid.UUID]:
    return set(session.scalars(select(Project.id).where(Project.course_id == course_id)))


def approved_among(session: Session, user_id: uuid.UUID, project_ids_: set[uuid.UUID]) -> set[uuid.UUID]:
    if not project_ids_:
        return set()
    return set(
        session.scalars(
            select(ProjectSubmission.project_id).where(
                ProjectSubmission.user_id == user_id,
                ProjectSubmission.status == "approved",
                ProjectSubmission.project_id.in_(project_ids_),
            )
        )
    )


def get_for_user(session: Session, user_id: uuid.UUID, course_id: uuid.UUID) -> Certificate | None:
    return session.scalar(select(Certificate).where(Certificate.user_id == user_id, Certificate.course_id == course_id))


def list_for_user(session: Session, user_id: uuid.UUID) -> dict[uuid.UUID, Certificate]:
    return {c.course_id: c for c in session.scalars(select(Certificate).where(Certificate.user_id == user_id))}


def get_by_code(session: Session, code: str) -> Certificate | None:
    return session.scalar(select(Certificate).where(Certificate.code == code))
