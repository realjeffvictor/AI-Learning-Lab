import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.models import AuditLog


def record(
    session: Session,
    action: str,
    actor_user_id: uuid.UUID | None = None,
    ip_address: str | None = None,
    details: dict[str, Any] | None = None,
) -> None:
    session.add(AuditLog(action=action, actor_user_id=actor_user_id, ip_address=ip_address, details=details or {}))
