import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.ai.provider import Completion
from app.core.errors import AppError
from app.main import create_app
from app.services import rate_limit_service

API = "/api/v1"
PASSWORD = "correct-horse-battery-staple"


def _register(client, n):
    return client.post(
        f"{API}/auth/register", json={"email": f"user{n}@example.com", "password": PASSWORD, "display_name": f"User {n}"}
    )


def test_service_counts_inside_the_window_only(db_engine):
    with Session(db_engine) as session:
        for _ in range(2):
            rate_limit_service.check(session, "t", "k", 2, 60)
        with pytest.raises(AppError) as caught:
            rate_limit_service.check(session, "t", "k", 2, 60)
        assert caught.value.status_code == 429 and int(caught.value.headers["Retry-After"]) >= 1
        rate_limit_service.check(session, "t", "other-key", 2, 60)
        rate_limit_service.check(session, "other-bucket", "k", 2, 60)


def test_old_hits_do_not_count_and_are_pruned(db_engine):
    with db_engine.begin() as connection:
        connection.execute(
            text("INSERT INTO rate_limit_hits (id, bucket, key, created_at) VALUES (gen_random_uuid(), 't', 'k', now() - interval '2 days')")
        )
    with Session(db_engine) as session:
        rate_limit_service.check(session, "t", "k", 1, 60, prune_probability=1.0)
    with db_engine.connect() as connection:
        assert connection.scalar(text("SELECT count(*) FROM rate_limit_hits WHERE created_at < now() - interval '1 day'")) == 0


def test_register_is_limited_per_ip(settings):
    strict = create_app(settings.model_copy(update={"rl_register_per_hour": 2}))
    with TestClient(strict) as client:
        assert [_register(client, i).status_code for i in range(3)] == [201, 201, 429]
        blocked = _register(client, 9)
    assert blocked.json()["error"]["code"] == "rate_limited" and int(blocked.headers["retry-after"]) > 0


def test_login_is_limited_per_ip(settings, client):
    assert _register(client, 1).status_code == 201
    strict = create_app(settings.model_copy(update={"rl_login_per_15min": 3}))
    bad = {"email": "user1@example.com", "password": "not-the-password"}
    with TestClient(strict) as limited:
        codes = [limited.post(f"{API}/auth/login", json=bad).status_code for _ in range(4)]
    assert codes == [401, 401, 401, 429]


def test_limits_can_be_switched_off(settings):
    open_app = create_app(settings.model_copy(update={"rl_register_per_hour": 1, "rate_limit_enabled": False}))
    with TestClient(open_app) as client:
        assert [_register(client, i).status_code for i in range(3)] == [201, 201, 201]


def test_ai_calls_are_limited_per_user(settings, make_user):
    class Fake:
        name = "fake"
        model = "fake-1"

        def complete(self, messages, max_output_tokens):
            return Completion("ok", 1, 1)

    user = make_user("a@example.com")
    strict = create_app(settings.model_copy(update={"rl_ai_per_minute": 2}))
    strict.state.ai_provider = Fake()
    body = {"assistant": "tutor", "mode": "hint", "message": "hi"}
    with TestClient(strict) as client:
        codes = [client.post(f"{API}/ai/chat", json=body, headers=user["headers"]).status_code for _ in range(3)]
    assert codes == [200, 200, 429]


def test_certificate_verification_is_limited_per_ip(settings):
    strict = create_app(settings.model_copy(update={"rl_verify_per_minute": 2}))
    with TestClient(strict) as client:
        codes = [client.get(f"{API}/certificates/verify/abcdefgh{i}").status_code for i in range(3)]
    assert codes == [404, 404, 429]
