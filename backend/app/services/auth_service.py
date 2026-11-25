import uuid
from dataclasses import dataclass
from datetime import timedelta

import jwt
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.errors import AppError
from app.core.security import (
    PasswordService,
    create_access_token,
    decode_access_token,
    hash_refresh_token,
    new_refresh_token,
    utcnow,
)
from app.core.throttle import LoginThrottle
from app.models import RefreshToken, User
from app.repositories import audit_repository, refresh_token_repository, user_repository
from app.services import user_service

_BEARER = {"WWW-Authenticate": "Bearer"}


@dataclass(frozen=True)
class AuthSession:
    user: User
    access_token: str
    expires_in: int
    refresh_token: str
    refresh_max_age: int


def _invalid_refresh() -> AppError:
    return AppError(401, "invalid_refresh_token", "Your session has expired. Please sign in again.", _BEARER)


class AuthService:
    def __init__(self, session: Session, settings: Settings, passwords: PasswordService, throttle: LoginThrottle):
        self.session = session
        self.settings = settings
        self.passwords = passwords
        self.throttle = throttle

    def register(self, *, email: str, password: str, display_name: str, ip: str | None) -> AuthSession:
        taken = AppError(409, "email_taken", "An account with this email already exists.")
        if user_repository.get_by_email(self.session, email):
            raise taken
        try:
            user = user_service.create_user(
                self.session, self.passwords, email=email, password=password, display_name=display_name
            )
            audit_repository.record(self.session, "auth.registered", actor_user_id=user.id, ip_address=ip)
            result = self._issue_session(user)
            self.session.commit()
        except IntegrityError:  # two simultaneous registrations of the same email
            self.session.rollback()
            raise taken from None
        return result

    def login(self, *, email: str, password: str, ip: str | None) -> AuthSession:
        throttle_key = f"{email}|{ip or 'unknown'}"
        wait = self.throttle.retry_after(throttle_key)
        if wait:
            raise AppError(
                429, "too_many_attempts", "Too many failed sign-in attempts. Try again later.", {"Retry-After": str(wait)}
            )

        user = user_repository.get_by_email(self.session, email)
        if user is None:
            self.passwords.verify_dummy(password)
            verified = False
        else:
            verified = self.passwords.verify(user.password_hash, password)

        if not verified:
            self.throttle.record_failure(throttle_key)
            audit_repository.record(
                self.session,
                "auth.login_failed",
                actor_user_id=user.id if user else None,
                ip_address=ip,
                details={"reason": "invalid_credentials"},
            )
            self.session.commit()
            raise AppError(401, "invalid_credentials", "Incorrect email or password.", _BEARER)

        assert user is not None
        if not user.is_active:
            audit_repository.record(self.session, "auth.login_blocked", actor_user_id=user.id, ip_address=ip)
            self.session.commit()
            raise AppError(403, "account_disabled", "This account has been deactivated.")

        self.throttle.reset(throttle_key)
        if self.passwords.needs_rehash(user.password_hash):
            user.password_hash = self.passwords.hash(password)
        user.last_login_at = utcnow()
        result = self._issue_session(user)
        audit_repository.record(self.session, "auth.login", actor_user_id=user.id, ip_address=ip)
        self.session.commit()
        return result

    def refresh(self, raw_token: str | None, ip: str | None) -> AuthSession:
        if not raw_token:
            raise _invalid_refresh()
        now = utcnow()
        token = refresh_token_repository.get_by_hash(self.session, hash_refresh_token(raw_token), for_update=True)
        if token is None:
            raise _invalid_refresh()

        if token.revoked_at is not None:
            age = (now - token.revoked_at).total_seconds()
            if age > self.settings.refresh_reuse_grace_seconds:
                # A rotated or logged-out token came back late: assume theft and end the whole session family.
                refresh_token_repository.revoke_family(self.session, token.family_id, now)
                audit_repository.record(
                    self.session, "auth.refresh_reuse_detected", actor_user_id=token.user_id, ip_address=ip
                )
                self.session.commit()
            raise _invalid_refresh()

        if token.expires_at <= now:
            raise _invalid_refresh()

        user = user_repository.get_by_id(self.session, token.user_id)
        if user is None or not user.is_active:
            refresh_token_repository.revoke_family(self.session, token.family_id, now)
            self.session.commit()
            raise _invalid_refresh()

        token.revoked_at = now
        result = self._issue_session(user, family_id=token.family_id)
        self.session.commit()
        return result

    def logout(self, raw_token: str | None, ip: str | None) -> None:
        if not raw_token:
            return
        token = refresh_token_repository.get_by_hash(self.session, hash_refresh_token(raw_token), for_update=True)
        if token is None:
            return
        refresh_token_repository.revoke_family(self.session, token.family_id, utcnow())
        audit_repository.record(self.session, "auth.logout", actor_user_id=token.user_id, ip_address=ip)
        self.session.commit()

    def authenticate_access_token(self, token: str) -> User:
        try:
            user_id = decode_access_token(token, self.settings)
        except jwt.InvalidTokenError:
            raise AppError(401, "invalid_token", "Invalid or expired access token.", _BEARER) from None
        user = user_repository.get_by_id(self.session, user_id)
        if user is None:
            raise AppError(401, "invalid_token", "Invalid or expired access token.", _BEARER)
        if not user.is_active:
            raise AppError(403, "account_disabled", "This account has been deactivated.")
        return user

    def _issue_session(self, user: User, family_id: uuid.UUID | None = None) -> AuthSession:
        now = utcnow()
        access_token, expires_in = create_access_token(user.id, self.settings, now)
        raw_refresh, refresh_hash = new_refresh_token()
        max_age = self.settings.refresh_token_days * 86400
        refresh_token_repository.add(
            self.session,
            RefreshToken(
                user_id=user.id,
                family_id=family_id or uuid.uuid4(),
                token_hash=refresh_hash,
                expires_at=now + timedelta(seconds=max_age),
            ),
        )
        return AuthSession(
            user=user,
            access_token=access_token,
            expires_in=expires_in,
            refresh_token=raw_refresh,
            refresh_max_age=max_age,
        )
