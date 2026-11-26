import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.models import Exercise, LessonProgress, Project, ProjectReview, ProjectSubmission, Submission, UserAchievement


def earned(session: Session, user_id: uuid.UUID) -> dict[str, datetime]:
    rows = session.execute(
        select(UserAchievement.achievement_key, UserAchievement.earned_at).where(UserAchievement.user_id == user_id)
    ).all()
    return {key: when for key, when in rows}


def insert_missing(session: Session, user_id: uuid.UUID, items: dict[str, datetime]) -> None:
    if not items:
        return
    session.execute(
        pg_insert(UserAchievement)
        .values([{"user_id": user_id, "achievement_key": key, "earned_at": when} for key, when in items.items()])
        .on_conflict_do_nothing(index_elements=["user_id", "achievement_key"])
    )


def first_lesson_completed(session: Session, user_id: uuid.UUID) -> datetime | None:
    return session.scalar(
        select(func.min(LessonProgress.completed_at)).where(
            LessonProgress.user_id == user_id, LessonProgress.status == "completed"
        )
    )


def first_exercise_passed(session: Session, user_id: uuid.UUID) -> datetime | None:
    return session.scalar(
        select(func.min(Submission.created_at)).where(Submission.user_id == user_id, Submission.passed.is_(True))
    )


def first_perfect_server_graded(session: Session, user_id: uuid.UUID) -> datetime | None:
    """Quizzes and puzzles only: their scores are computed by the server, so they cannot be self-reported."""
    return session.scalar(
        select(func.min(Submission.created_at))
        .select_from(Submission)
        .join(Exercise, Exercise.id == Submission.exercise_id)
        .where(Submission.user_id == user_id, Submission.score == 100, Exercise.kind.in_(("quiz", "puzzle")))
    )


def first_project_submitted(session: Session, user_id: uuid.UUID) -> datetime | None:
    return session.scalar(
        select(func.min(ProjectSubmission.submitted_at)).where(
            ProjectSubmission.user_id == user_id, ProjectSubmission.submitted_at.is_not(None)
        )
    )


def first_project_approved(session: Session, user_id: uuid.UUID, kind: str) -> datetime | None:
    return session.scalar(
        select(func.min(ProjectReview.created_at))
        .select_from(ProjectReview)
        .join(ProjectSubmission, ProjectSubmission.id == ProjectReview.submission_id)
        .join(Project, Project.id == ProjectSubmission.project_id)
        .where(
            ProjectSubmission.user_id == user_id,
            ProjectReview.outcome == "approved",
            Project.kind == kind,
        )
    )
