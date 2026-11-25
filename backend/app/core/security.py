import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from functools import cached_property

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from app.core.config import Settings

MIN_PASSWORD_LENGTH = 10
MAX_PASSWORD_LENGTH = 128
MIN_SECRET_LENGTH = 32


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def check_password_policy(password: str, email: str | None = None) -> str | None:
    """Return a human-readable problem, or None when the password is acceptable."""
    if len(password) < MIN_PASSWORD_LENGTH:
        return f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
    if len(password) > MAX_PASSWORD_LENGTH:
        return f"Password must be at most {MAX_PASSWORD_LENGTH} characters."
    if not password.strip():
        return "Password cannot be only whitespace."
    if email and password.lower() == email.lower():
        return "Password must not be your email address."
    return None


class PasswordService:
    """Argon2id hashing. Parameters come from settings so tests can use cheap ones."""

    def __init__(self, time_cost: int, memory_kib: int, parallelism: int) -> None:
        self._hasher = PasswordHasher(time_cost=time_cost, memory_cost=memory_kib, parallelism=parallelism)

    @classmethod
    def from_settings(cls, settings: Settings) -> "PasswordService":
        return cls(settings.argon2_time_cost, settings.argon2_memory_kib, settings.argon2_parallelism)

    @cached_property
    def _dummy_hash(self) -> str:
        return self._hasher.hash("timing-equalizer-not-a-real-password")

    def hash(self, password: str) -> str:
        return self._hasher.hash(password)

    def verify(self, password_hash: str, password: str) -> bool:
        try:
            return self._hasher.verify(password_hash, password)
        except (VerificationError, InvalidHashError):
            return False

    def verify_dummy(self, password: str) -> None:
        """Spend the same time as a real verification so unknown emails are not detectable by timing."""
        self.verify(self._dummy_hash, password)

    def needs_rehash(self, password_hash: str) -> bool:
        return self._hasher.check_needs_rehash(password_hash)


def _require_secret(settings: Settings) -> str:
    if len(settings.jwt_secret) < MIN_SECRET_LENGTH:
        raise RuntimeError("JWT_SECRET is not configured (needs at least 32 characters). Run scripts/setup_db.sh.")
    return settings.jwt_secret


def create_access_token(user_id: uuid.UUID, settings: Settings, now: datetime | None = None) -> tuple[str, int]:
    """Return (token, lifetime_seconds). The token carries no role: roles are always read from the database."""
    secret = _require_secret(settings)
    issued = now or utcnow()
    expires = issued + timedelta(minutes=settings.access_token_minutes)
    claims = {"sub": str(user_id), "iat": issued, "exp": expires, "type": "access", "jti": uuid.uuid4().hex}
    token = jwt.encode(claims, secret, algorithm=settings.jwt_algorithm)
    return token, settings.access_token_minutes * 60


def decode_access_token(token: str, settings: Settings) -> uuid.UUID:
    """Return the user id or raise jwt.InvalidTokenError."""
    secret = _require_secret(settings)
    payload = jwt.decode(
        token,
        secret,
        algorithms=[settings.jwt_algorithm],
        options={"require": ["exp", "iat", "sub"]},
    )
    if payload.get("type") != "access":
        raise jwt.InvalidTokenError("Wrong token type.")
    try:
        return uuid.UUID(payload["sub"])
    except (ValueError, TypeError) as exc:
        raise jwt.InvalidTokenError("Invalid subject.") from exc


def hash_refresh_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def new_refresh_token() -> tuple[str, str]:
    """Return (raw_token_for_cookie, sha256_hash_for_database)."""
    raw = secrets.token_urlsafe(48)
    return raw, hash_refresh_token(raw)
