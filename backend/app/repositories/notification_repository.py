import uuid
from datetime import datetime

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.models import Notification


def add(session: Session, user_id: uuid.UUID, kind: str, title: str, body: str, link: str | None) -> None:
    session.add(Notification(user_id=user_id, kind=kind, title=title[:200], body=body[:500], link=link))


def list_for_user(session: Session, user_id: uuid.UUID, limit: int) -> list[Notification]:
    return list(
        session.scalars(
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc(), Notification.id.desc())
            .limit(limit)
        )
    )


def unread_count(session: Session, user_id: uuid.UUID) -> int:
    return int(
        session.scalar(
            select(func.count(Notification.id)).where(Notification.user_id == user_id, Notification.read_at.is_(None))
        )
        or 0
    )


def get_owned(session: Session, user_id: uuid.UUID, notification_id: uuid.UUID) -> Notification | None:
    return session.scalar(
        select(Notification).where(Notification.id == notification_id, Notification.user_id == user_id)
    )


def mark_all_read(session: Session, user_id: uuid.UUID, now: datetime) -> None:
    session.execute(
        update(Notification)
        .where(Notification.user_id == user_id, Notification.read_at.is_(None))
        .values(read_at=now)
    )
