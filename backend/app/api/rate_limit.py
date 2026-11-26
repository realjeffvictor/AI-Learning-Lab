from collections.abc import Callable

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import client_ip, get_current_user, get_db
from app.core.config import Settings
from app.core.deps import get_app_settings
from app.models import User
from app.services import rate_limit_service


def ip_rate_limit(bucket: str, setting: str, window_seconds: int) -> Callable[..., None]:
    """Dependency factory: limit by client IP. `setting` names the Settings field holding the limit."""

    def dependency(
        request: Request,
        db: Session = Depends(get_db),
        settings: Settings = Depends(get_app_settings),
    ) -> None:
        if settings.rate_limit_enabled:
            rate_limit_service.check(db, bucket, client_ip(request) or "unknown", getattr(settings, setting), window_seconds)

    return dependency


def user_rate_limit(bucket: str, setting: str, window_seconds: int) -> Callable[..., None]:
    """Dependency factory: limit by signed-in user. Unauthenticated callers get a 401 first."""

    def dependency(
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
        settings: Settings = Depends(get_app_settings),
    ) -> None:
        if settings.rate_limit_enabled:
            rate_limit_service.check(db, bucket, str(user.id), getattr(settings, setting), window_seconds)

    return dependency
