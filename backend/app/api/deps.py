from collections.abc import Callable, Iterator

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.deps import get_app_settings
from app.core.errors import AppError
from app.models import User
from app.services.auth_service import AuthService

bearer_scheme = HTTPBearer(auto_error=False)


def get_db(request: Request) -> Iterator[Session]:
    factory = request.app.state.session_factory
    if factory is None:
        raise AppError(503, "database_unavailable", "The database is not configured.")
    session = factory()
    try:
        yield session
    finally:
        session.close()


def get_auth_service(
    request: Request,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_app_settings),
) -> AuthService:
    return AuthService(db, settings, request.app.state.passwords, request.app.state.login_throttle)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    service: AuthService = Depends(get_auth_service),
) -> User:
    if credentials is None:
        raise AppError(401, "not_authenticated", "Authentication required.", {"WWW-Authenticate": "Bearer"})
    return service.authenticate_access_token(credentials.credentials)


def require_roles(*roles: str) -> Callable[..., User]:
    """The authoritative permission check. Frontend route guards are cosmetic only."""

    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise AppError(403, "forbidden", "You do not have permission to perform this action.")
        return user

    return checker


def require_csrf_header(request: Request) -> None:
    """Cookie-authenticated endpoints need a custom header, which cross-site pages cannot send."""
    if request.headers.get("x-csrf-protection") != "1":
        raise AppError(403, "csrf_failed", "Missing CSRF protection header.")


def client_ip(request: Request) -> str | None:
    return request.client.host if request.client else None
