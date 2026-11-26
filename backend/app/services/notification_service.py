import uuid

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.security import utcnow
from app.models import ProjectSubmission
from app.repositories import notification_repository, project_repository
from app.schemas.notification import NotificationList, NotificationRead


def create(session: Session, user_id: uuid.UUID, kind: str, title: str, body: str = "", link: str | None = None) -> None:
    """Adds a notification. The caller commits."""
    notification_repository.add(session, user_id, kind, title, body, link)


def notify_review(session: Session, submission: ProjectSubmission, outcome: str) -> None:
    row = project_repository.get_project_with_course_by_id(session, submission.project_id)
    if row is None:
        return
    project, course = row
    title = (
        f"Your project was approved: {project.title}"
        if outcome == "approved"
        else f"Changes requested on {project.title}"
    )
    create(
        session,
        submission.user_id,
        "project_reviewed",
        title,
        "Open the project to read the reviewer's feedback.",
        f"/projects/{course.slug}/{project.slug}",
    )


def list_for_user(session: Session, user_id: uuid.UUID, limit: int = 30) -> NotificationList:
    items = [NotificationRead.model_validate(n) for n in notification_repository.list_for_user(session, user_id, limit)]
    return NotificationList(items=items, unread_count=notification_repository.unread_count(session, user_id))


def unread_count(session: Session, user_id: uuid.UUID) -> int:
    return notification_repository.unread_count(session, user_id)


def mark_read(session: Session, user_id: uuid.UUID, notification_id: uuid.UUID) -> None:
    notification = notification_repository.get_owned(session, user_id, notification_id)
    if notification is None:
        raise AppError(404, "notification_not_found", "Notification not found.")
    if notification.read_at is None:
        notification.read_at = utcnow()
        session.commit()


def mark_all_read(session: Session, user_id: uuid.UUID) -> None:
    notification_repository.mark_all_read(session, user_id, utcnow())
    session.commit()
