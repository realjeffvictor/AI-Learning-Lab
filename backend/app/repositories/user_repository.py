import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import User


def get_by_id(session: Session, user_id: uuid.UUID) -> User | None:
    return session.get(User, user_id)


def get_by_email(session: Session, email: str) -> User | None:
    return session.scalar(select(User).where(User.email == email))


def add(session: Session, user: User) -> User:
    session.add(user)
    session.flush()  # assigns the id and surfaces constraint violations immediately
    return user


def list_page(session: Session, page: int, page_size: int) -> tuple[list[User], int]:
    total = session.scalar(select(func.count()).select_from(User)) or 0
    statement = (
        select(User).order_by(User.created_at.desc(), User.id).limit(page_size).offset((page - 1) * page_size)
    )
    return list(session.scalars(statement).unique().all()), total
