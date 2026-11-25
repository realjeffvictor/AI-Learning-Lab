import uuid
from datetime import timedelta

import jwt
import pytest

from app.core.config import Settings
from app.core.security import (
    PasswordService,
    check_password_policy,
    create_access_token,
    decode_access_token,
    hash_refresh_token,
    new_refresh_token,
    utcnow,
)
from app.core.throttle import LoginThrottle


def _hasher() -> PasswordService:
    return PasswordService(time_cost=1, memory_kib=8192, parallelism=1)


def test_password_hash_verifies():
    hasher = _hasher()
    hashed = hasher.hash("correct-horse-battery-staple")
    assert hashed.startswith("$argon2id$")
    assert hasher.verify(hashed, "correct-horse-battery-staple")


def test_wrong_password_does_not_verify():
    hasher = _hasher()
    assert not hasher.verify(hasher.hash("correct-horse-battery-staple"), "wrong")


def test_hashes_are_salted():
    hasher = _hasher()
    assert hasher.hash("same-password-123") != hasher.hash("same-password-123")


def test_garbage_hash_does_not_verify_or_raise():
    assert not _hasher().verify("not-a-hash", "anything")


def test_needs_rehash_when_parameters_get_stronger():
    weak = _hasher()
    stronger = PasswordService(time_cost=2, memory_kib=8192, parallelism=1)
    assert stronger.needs_rehash(weak.hash("some-long-password"))
    assert not weak.needs_rehash(weak.hash("some-long-password"))


@pytest.mark.parametrize(
    ("password", "email", "problem"),
    [
        ("short", None, "at least"),
        ("x" * 129, None, "at most"),
        ("            ", None, "whitespace"),
        ("user@example.com", "USER@example.com", "email"),
        ("a-perfectly-fine-passphrase", "user@example.com", None),
    ],
)
def test_password_policy(password, email, problem):
    result = check_password_policy(password, email)
    if problem is None:
        assert result is None
    else:
        assert result is not None and problem in result


def test_access_token_round_trip(settings):
    user_id = uuid.uuid4()
    token, lifetime = create_access_token(user_id, settings)
    assert lifetime == settings.access_token_minutes * 60
    assert decode_access_token(token, settings) == user_id


def test_token_of_wrong_type_is_rejected(settings):
    now = utcnow()
    token = jwt.encode(
        {"sub": str(uuid.uuid4()), "iat": now, "exp": now + timedelta(minutes=5), "type": "refresh"},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(token, settings)


def test_short_or_missing_secret_is_refused():
    weak = Settings(environment="test", jwt_secret="short", _env_file=None)
    with pytest.raises(RuntimeError):
        create_access_token(uuid.uuid4(), weak)


def test_refresh_token_helpers():
    raw_a, hash_a = new_refresh_token()
    raw_b, hash_b = new_refresh_token()
    assert raw_a != raw_b and hash_a != hash_b
    assert hash_a == hash_refresh_token(raw_a)
    assert len(hash_a) == 64 and raw_a not in hash_a


class FakeClock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


def test_throttle_blocks_after_max_failures():
    throttle = LoginThrottle(3, 60, FakeClock())
    for _ in range(2):
        throttle.record_failure("k")
    assert throttle.retry_after("k") == 0
    throttle.record_failure("k")
    assert throttle.retry_after("k") > 0


def test_throttle_window_expires():
    clock = FakeClock()
    throttle = LoginThrottle(2, 60, clock)
    throttle.record_failure("k")
    throttle.record_failure("k")
    assert throttle.retry_after("k") > 0
    clock.now += 61
    assert throttle.retry_after("k") == 0


def test_throttle_reset_clears_failures():
    throttle = LoginThrottle(1, 60, FakeClock())
    throttle.record_failure("k")
    throttle.reset("k")
    assert throttle.retry_after("k") == 0


def test_throttle_keys_are_independent():
    throttle = LoginThrottle(1, 60, FakeClock())
    throttle.record_failure("a")
    assert throttle.retry_after("a") > 0
    assert throttle.retry_after("b") == 0
