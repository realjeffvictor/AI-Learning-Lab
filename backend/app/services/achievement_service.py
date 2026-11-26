"""Achievements are derived from evidence already in the database. earned_at is the evidence time, not the time of the check."""
import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session

from app.repositories import achievement_repository as repo
from app.schemas.project import AchievementRead


@dataclass(frozen=True)
class AchievementDef:
    key: str
    title: str
    description: str


CATALOG = (
    AchievementDef("first-lesson", "First lesson", "Completed your first lesson."),
    AchievementDef("first-pass", "First pass", "Passed your first exercise."),
    AchievementDef("perfect-score", "Perfect score", "Scored 100 on a quiz or puzzle."),
    AchievementDef("first-project-submitted", "Shipped for review", "Submitted your first project."),
    AchievementDef("builder", "Builder", "Had a build project approved by a reviewer."),
    AchievementDef("architect", "Architect", "Had an architecture project approved by a reviewer."),
    AchievementDef("reviewer", "Code reviewer", "Had a code review project approved by a reviewer."),
)


def _evidence(session: Session, user_id: uuid.UUID) -> dict[str, datetime | None]:
    return {
        "first-lesson": repo.first_lesson_completed(session, user_id),
        "first-pass": repo.first_exercise_passed(session, user_id),
        "perfect-score": repo.first_perfect_server_graded(session, user_id),
        "first-project-submitted": repo.first_project_submitted(session, user_id),
        "builder": repo.first_project_approved(session, user_id, "build"),
        "architect": repo.first_project_approved(session, user_id, "architecture"),
        "reviewer": repo.first_project_approved(session, user_id, "code_review"),
    }


def sync(session: Session, user_id: uuid.UUID) -> dict[str, datetime]:
    """Store any newly earned achievements (idempotent) and return everything earned. The caller commits."""
    session.flush()
    already = repo.earned(session, user_id)
    new = {key: when for key, when in _evidence(session, user_id).items() if when is not None and key not in already}
    repo.insert_missing(session, user_id, new)
    return {**already, **new}


def list_for_user(session: Session, user_id: uuid.UUID) -> list[AchievementRead]:
    earned = sync(session, user_id)
    session.commit()
    return [
        AchievementRead(
            key=item.key,
            title=item.title,
            description=item.description,
            earned=item.key in earned,
            earned_at=earned.get(item.key),
        )
        for item in CATALOG
    ]
