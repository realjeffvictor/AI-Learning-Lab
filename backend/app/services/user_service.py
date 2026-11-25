import uuid
from collections.abc import Mapping
from typing import Any

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.security import PasswordService, utcnow
from app.models import User, UserProfile
from app.repositories import audit_repository, refresh_token_repository, user_repository

_PROFILE_FIELDS = {"display_name", "bio", "experience_level"}


def create_user(
    session: Session,
    passwords: PasswordService,
    *,
    email: str,
    password: str,
    display_name: str,
    role: str = "student",
) -> User:
    """Create a user and profile (flushed, not committed). The caller owns the transaction."""
    user = User(email=email, password_hash=passwords.hash(password), role=role)
    user.profile = UserProfile(display_name=display_name)
    return user_repository.add(session, user)


def update_profile(session: Session, user: User, changes: Mapping[str, Any]) -> User:
    for field, value in changes.items():
        if field in _PROFILE_FIELDS:
            setattr(user.profile, field, value)
    session.commit()
    return user


def list_users(session: Session, page: int, page_size: int) -> tuple[list[User], int]:
    return user_repository.list_page(session, page, page_size)


def admin_update_user(
    session: Session,
    actor: User,
    target_id: uuid.UUID,
    changes: Mapping[str, Any],
    ip_address: str | None,
) -> User:
    if target_id == actor.id:
        raise AppError(400, "cannot_modify_self", "You cannot change your own role or status.")
    target = user_repository.get_by_id(session, target_id)
    if target is None:
        raise AppError(404, "user_not_found", "User not found.")

    now = utcnow()
    new_role = changes.get("role")
    if new_role is not None and new_role != target.role:
        previous = target.role
        target.role = new_role
        audit_repository.record(
            session,
            "user.role_changed",
            actor_user_id=actor.id,
            ip_address=ip_address,
            details={"target_user_id": str(target.id), "from": previous, "to": new_role},
        )

    new_active = changes.get("is_active")
    if new_active is not None and new_active != target.is_active:
        target.is_active = new_active
        if not new_active:
            refresh_token_repository.revoke_all_for_user(session, target.id, now)
        audit_repository.record(
            session,
            "user.reactivated" if new_active else "user.deactivated",
            actor_user_id=actor.id,
            ip_address=ip_address,
            details={"target_user_id": str(target.id)},
        )

    session.commit()
    return target
