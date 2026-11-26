import uuid
from datetime import date, datetime

from sqlalchemy import delete, distinct, func, or_, select, union
from sqlalchemy.orm import Session

from app.models import (
    AIUsageCounter,
    Course,
    Enrollment,
    Exercise,
    Lesson,
    LessonProgress,
    Module,
    ProjectSubmission,
    Submission,
    User,
    UserProfile,
)


def users_by_role(session: Session) -> dict[str, int]:
    return {role: int(count) for role, count in session.execute(select(User.role, func.count(User.id)).group_by(User.role))}


def active_learners(session: Session, since: datetime) -> int:
    active = union(
        select(LessonProgress.user_id).where(LessonProgress.last_visited_at >= since),
        select(Submission.user_id).where(Submission.created_at >= since),
    ).subquery()
    return int(session.scalar(select(func.count()).select_from(active)) or 0)


def pending_reviews(session: Session) -> int:
    return int(
        session.scalar(select(func.count(ProjectSubmission.id)).where(ProjectSubmission.status == "submitted")) or 0
    )


def enrollment_counts(session: Session):
    return session.execute(
        select(Course.slug, Course.title, func.count(Enrollment.id))
        .select_from(Course)
        .outerjoin(Enrollment, Enrollment.course_id == Course.id)
        .group_by(Course.id)
        .order_by(Course.position)
    ).all()


def top_lessons(session: Session, limit: int):
    completed = func.count(LessonProgress.id)
    return session.execute(
        select(Course.slug, Module.slug, Lesson.slug, Lesson.title, completed)
        .select_from(LessonProgress)
        .join(Lesson, Lesson.id == LessonProgress.lesson_id)
        .join(Module, Module.id == Lesson.module_id)
        .join(Course, Course.id == Module.course_id)
        .where(LessonProgress.status == "completed")
        .group_by(Lesson.id, Module.id, Course.id)
        .order_by(completed.desc(), Lesson.title)
        .limit(limit)
    ).all()


def exercise_stats(session: Session, limit: int):
    attempts = func.count(Submission.id)
    learners = func.count(distinct(Submission.user_id))
    passed = func.count(distinct(Submission.user_id)).filter(Submission.passed.is_(True))
    return session.execute(
        select(Exercise.id, Exercise.title, Exercise.kind, Lesson.title, attempts, learners, passed)
        .select_from(Submission)
        .join(Exercise, Exercise.id == Submission.exercise_id)
        .join(Lesson, Lesson.id == Exercise.lesson_id)
        .group_by(Exercise.id, Lesson.id)
        .order_by(attempts.desc(), Exercise.title)
        .limit(limit)
    ).all()


def ai_usage(session: Session, today: date, since: date) -> tuple[int, int, int]:
    """Returns (requests today, requests since, tokens since)."""
    requests_today = session.scalar(
        select(func.coalesce(func.sum(AIUsageCounter.requests), 0)).where(AIUsageCounter.day == today)
    )
    row = session.execute(
        select(
            func.coalesce(func.sum(AIUsageCounter.requests), 0),
            func.coalesce(func.sum(AIUsageCounter.tokens_in + AIUsageCounter.tokens_out), 0),
        ).where(AIUsageCounter.day >= since)
    ).one()
    return int(requests_today or 0), int(row[0]), int(row[1])


def _escape_like(text: str) -> str:
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def student_page(session: Session, page: int, page_size: int, q: str | None, role: str | None):
    conditions = []
    if role:
        conditions.append(User.role == role)
    if q and q.strip():
        pattern = f"%{_escape_like(q.strip())}%"
        conditions.append(or_(User.email.ilike(pattern, escape="\\"), UserProfile.display_name.ilike(pattern, escape="\\")))

    total = session.scalar(
        select(func.count())
        .select_from(User)
        .join(UserProfile, UserProfile.user_id == User.id)
        .where(*conditions)
    )
    completed = (
        select(func.count(LessonProgress.id))
        .where(LessonProgress.user_id == User.id, LessonProgress.status == "completed")
        .scalar_subquery()
    )
    enrolled = select(func.count(Enrollment.id)).where(Enrollment.user_id == User.id).scalar_subquery()
    last_active = select(func.max(LessonProgress.last_visited_at)).where(LessonProgress.user_id == User.id).scalar_subquery()
    rows = session.execute(
        select(
            User.id,
            User.email,
            User.role,
            User.is_active,
            User.created_at,
            UserProfile.display_name,
            completed.label("lessons_completed"),
            enrolled.label("enrollments"),
            last_active.label("last_active_at"),
        )
        .select_from(User)
        .join(UserProfile, UserProfile.user_id == User.id)
        .where(*conditions)
        .order_by(User.created_at.desc(), User.id)
        .limit(page_size)
        .offset((page - 1) * page_size)
    ).all()
    return rows, int(total or 0)


def exercise_summary(session: Session, user_id: uuid.UUID) -> tuple[int, int]:
    """Returns (attempts, number of different exercises passed)."""
    row = session.execute(
        select(
            func.count(Submission.id),
            func.count(distinct(Submission.exercise_id)).filter(Submission.passed.is_(True)),
        ).where(Submission.user_id == user_id)
    ).one()
    return int(row[0]), int(row[1])


def delete_enrollment(session: Session, user_id: uuid.UUID, course_id: uuid.UUID) -> int:
    result = session.execute(
        delete(Enrollment).where(Enrollment.user_id == user_id, Enrollment.course_id == course_id)
    )
    return result.rowcount
