import uuid
from datetime import timedelta

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.security import utcnow
from app.models import User
from app.repositories import (
    audit_repository,
    curriculum_repository,
    progress_repository,
    staff_repository,
    user_repository,
)
from app.schemas.curriculum import EnrollmentRead
from app.schemas.manage import (
    AIUsageStat,
    EnrollmentCount,
    ExerciseStat,
    LessonCompletion,
    Overview,
    StudentDetail,
    StudentPage,
    StudentRow,
)
from app.schemas.user import UserRead
from app.services import assessment_service, curriculum_service, notification_service, project_service


def overview(session: Session) -> Overview:
    now = utcnow()
    since = now - timedelta(days=7)
    requests_today, requests_7d, tokens_7d = staff_repository.ai_usage(session, now.date(), since.date())
    return Overview(
        users_by_role=staff_repository.users_by_role(session),
        active_learners_7d=staff_repository.active_learners(session, since),
        pending_reviews=staff_repository.pending_reviews(session),
        enrollments=[
            EnrollmentCount(course_slug=slug, course_title=title, enrolled=int(count))
            for slug, title, count in staff_repository.enrollment_counts(session)
        ],
        top_lessons=[
            LessonCompletion(course_slug=c, module_slug=m, lesson_slug=l, title=title, completed=int(n))
            for c, m, l, title, n in staff_repository.top_lessons(session, 10)
        ],
        exercises=[
            ExerciseStat(
                exercise_id=eid, title=title, kind=kind, lesson_title=lesson_title,
                attempts=int(attempts), learners=int(learners), passed_learners=int(passed),
            )
            for eid, title, kind, lesson_title, attempts, learners, passed in staff_repository.exercise_stats(session, 15)
        ],
        ai=AIUsageStat(requests_today=requests_today, requests_7d=requests_7d, tokens_7d=tokens_7d),
    )


def list_students(session: Session, page: int, page_size: int, q: str | None, role: str | None) -> StudentPage:
    rows, total = staff_repository.student_page(session, page, page_size, q, role)
    items = [
        StudentRow(
            id=row.id,
            email=row.email,
            display_name=row.display_name,
            role=row.role,
            is_active=row.is_active,
            created_at=row.created_at,
            lessons_completed=int(row.lessons_completed or 0),
            enrollments=int(row.enrollments or 0),
            last_active_at=row.last_active_at,
        )
        for row in rows
    ]
    return StudentPage(items=items, page=page, page_size=page_size, total=total)


def _get_user(session: Session, user_id: uuid.UUID) -> User:
    user = user_repository.get_by_id(session, user_id)
    if user is None:
        raise AppError(404, "user_not_found", "User not found.")
    return user


def student_detail(session: Session, user_id: uuid.UUID) -> StudentDetail:
    user = _get_user(session, user_id)
    attempts, passed = staff_repository.exercise_summary(session, user.id)
    return StudentDetail(
        user=UserRead.model_validate(user),
        lessons_completed=progress_repository.completed_lesson_total(session, user.id),
        time_spent_seconds=progress_repository.total_time_seconds(session, user.id),
        exercise_attempts=attempts,
        exercises_passed=passed,
        courses=curriculum_service.list_courses(session, user.id),
        projects=project_service.list_projects(session, user.id),
        mastery=assessment_service.mastery(session, user.id),
    )


def enroll(session: Session, actor: User, user_id: uuid.UUID, course_slug: str, ip: str | None) -> EnrollmentRead:
    user = _get_user(session, user_id)
    course = curriculum_repository.get_course_basic(session, course_slug)
    if course is None:
        raise AppError(404, "course_not_found", "Course not found.")
    already = progress_repository.get_enrollment(session, user.id, course.id) is not None
    progress_repository.ensure_enrollment(session, user.id, course.id)
    if not already:
        notification_service.create(
            session, user.id, "enrolled", f"You were enrolled in {course.title}", "", f"/courses/{course.slug}"
        )
        audit_repository.record(
            session, "enrollment.added", actor_user_id=actor.id, ip_address=ip,
            details={"user_id": str(user.id), "course": course.slug},
        )
    session.commit()
    enrollment = progress_repository.get_enrollment(session, user.id, course.id)
    assert enrollment is not None
    return EnrollmentRead(course_slug=course.slug, enrolled_at=enrollment.created_at)


def unenroll(session: Session, actor: User, user_id: uuid.UUID, course_slug: str, ip: str | None) -> None:
    user = _get_user(session, user_id)
    course = curriculum_repository.get_course_basic(session, course_slug)
    if course is None:
        raise AppError(404, "course_not_found", "Course not found.")
    if staff_repository.delete_enrollment(session, user.id, course.id):
        audit_repository.record(
            session, "enrollment.removed", actor_user_id=actor.id, ip_address=ip,
            details={"user_id": str(user.id), "course": course.slug},
        )
    session.commit()
