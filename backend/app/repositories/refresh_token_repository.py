import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models import RefreshToken


def add(session: Session, token: RefreshToken) -> None:
    session.add(token)


def get_by_hash(session: Session, token_hash: str, for_update: bool = False) -> RefreshToken | None:
    statement = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    if for_update:
        statement = statement.with_for_update()  # serialises concurrent rotations of the same token
    return session.scalar(statement)


def revoke_family(session: Session, family_id: uuid.UUID, now: datetime) -> None:
    session.execute(
        update(RefreshToken)
        .where(RefreshToken.family_id == family_id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=now)
    )


def revoke_all_for_user(session: Session, user_id: uuid.UUID, now: datetime) -> None:
    session.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=now)
    )
