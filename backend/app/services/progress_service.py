import uuid

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.security import utcnow
from app.models import Lesson, LessonProgress
from app.repositories import curriculum_repository, progress_repository
from app.schemas.curriculum import LessonProgressRead
from app.schemas.progress import CompetencyRead, ProgressSummary, UpNext
from app.services import curriculum_service

# A heartbeat may claim at most the wall-clock time since the previous one, plus this slack for network jitter.
TIME_SLACK_SECONDS = 5


def _read(progress: LessonProgress) -> LessonProgressRead:
    return LessonProgressRead(
        status=progress.status,
        time_spent_seconds=progress.time_spent_seconds,
        completed_at=progress.completed_at,
    )


def _published_lesson(session: Session, lesson_id: uuid.UUID) -> Lesson:
    lesson = curriculum_repository.get_lesson_by_id(session, lesson_id)
    if lesson is None:
        raise AppError(404, "lesson_not_found", "Lesson not found.")
    if lesson.status != "published":
        raise AppError(409, "lesson_unavailable", "This lesson has not been published yet.")
    return lesson


def _ensure_started(session: Session, user_id: uuid.UUID, lesson: Lesson) -> LessonProgress:
    """Starting a lesson also enrols the learner in its course. Returns the locked progress row."""
    now = utcnow()
    module = curriculum_repository.get_module(session, lesson.module_id)
    assert module is not None
    progress_repository.ensure_enrollment(session, user_id, module.course_id)
    progress_repository.ensure_progress(session, user_id, lesson.id, now)
    progress = progress_repository.get_progress(session, user_id, lesson.id, for_update=True)
    assert progress is not None
    return progress


def start_lesson(session: Session, user_id: uuid.UUID, lesson_id: uuid.UUID) -> LessonProgressRead:
    lesson = _published_lesson(session, lesson_id)
    progress = _ensure_started(session, user_id, lesson)
    progress.last_visited_at = utcnow()
    session.commit()
    return _read(progress)


def add_time(session: Session, user_id: uuid.UUID, lesson_id: uuid.UUID, seconds: int) -> LessonProgressRead:
    progress = progress_repository.get_progress(session, user_id, lesson_id, for_update=True)
    if progress is None:
        raise AppError(409, "progress_not_started", "Start the lesson before recording time.")
    now = utcnow()
    elapsed = max(0.0, (now - progress.last_visited_at).total_seconds())
    progress.time_spent_seconds += min(seconds, int(elapsed) + TIME_SLACK_SECONDS)
    progress.last_visited_at = now
    session.commit()
    return _read(progress)


def complete_lesson(session: Session, user_id: uuid.UUID, lesson_id: uuid.UUID) -> LessonProgressRead:
    lesson = _published_lesson(session, lesson_id)
    progress = _ensure_started(session, user_id, lesson)
    now = utcnow()
    if progress.status != "completed":
        progress.status = "completed"
        progress.completed_at = now
        progress_repository.add_competency_evidence(
            session, user_id, curriculum_repository.lesson_concept_ids(session, lesson.id)
        )
    progress.last_visited_at = now
    session.commit()
    return _read(progress)


def get_summary(session: Session, user_id: uuid.UUID) -> ProgressSummary:
    row = progress_repository.in_progress_lesson(session, user_id)
    reason = "continue"
    if row is None:
        row = progress_repository.next_unfinished_lesson(session, user_id)
        reason = "start"
    up_next = (
        UpNext(
            reason=reason,
            course_slug=row.course_slug,
            course_title=row.course_title,
            module_slug=row.module_slug,
            lesson_slug=row.lesson_slug,
            lesson_title=row.lesson_title,
        )
        if row
        else None
    )
    return ProgressSummary(
        lessons_completed=progress_repository.completed_lesson_total(session, user_id),
        time_spent_seconds=progress_repository.total_time_seconds(session, user_id),
        courses=curriculum_service.list_courses(session, user_id),
        competencies=[
            CompetencyRead(slug=slug, name=name, category=category, lessons_completed=count)
            for slug, name, category, count in progress_repository.competencies(session, user_id)
        ],
        up_next=up_next,
    )
