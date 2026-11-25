import uuid
from datetime import timedelta

import jwt
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.security import create_access_token, utcnow
from app.main import create_app

PASSWORD = "correct-horse-battery-staple"
CSRF = {"X-CSRF-Protection": "1"}
COOKIE = "ail_refresh"


def _register(client, email="student@example.com", name="Ada Lovelace"):
    return client.post(
        "/api/v1/auth/register", json={"email": email, "password": PASSWORD, "display_name": name}
    )


def test_register_creates_student_session(client):
    response = _register(client)
    assert response.status_code == 201
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["user"]["role"] == "student"
    assert body["user"]["profile"]["display_name"] == "Ada Lovelace"
    assert "password" not in response.text
    assert response.headers["cache-control"] == "no-store"
    assert client.cookies.get(COOKIE)


def test_register_sets_hardened_cookie(client):
    cookie = _register(client).headers["set-cookie"].lower()
    assert "httponly" in cookie
    assert "samesite=lax" in cookie
    assert "path=/api/v1/auth" in cookie


def test_register_rejects_role_in_payload(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "evil@example.com", "password": PASSWORD, "display_name": "Evil", "role": "admin"},
    )
    assert response.status_code == 422


def test_register_duplicate_email_is_case_insensitive(client):
    assert _register(client, "student@example.com").status_code == 201
    response = _register(client, "Student@Example.com")
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "email_taken"


def test_register_rejects_weak_password_without_echoing_it(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "weak@example.com", "password": "weakpw1", "display_name": "Weak"},
    )
    assert response.status_code == 422
    assert "weakpw1" not in response.text


def test_login_success_records_last_login(client):
    _register(client)
    response = client.post("/api/v1/auth/login", json={"email": "student@example.com", "password": PASSWORD})
    assert response.status_code == 200
    assert response.json()["user"]["last_login_at"] is not None


def test_login_failures_look_identical_for_wrong_password_and_unknown_email(client):
    _register(client)
    wrong = client.post("/api/v1/auth/login", json={"email": "student@example.com", "password": "not-the-password"})
    unknown = client.post("/api/v1/auth/login", json={"email": "nobody@example.com", "password": PASSWORD})
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json()["error"]["code"] == unknown.json()["error"]["code"] == "invalid_credentials"
    assert wrong.json()["error"]["message"] == unknown.json()["error"]["message"]


def test_login_email_is_case_insensitive(client):
    _register(client, "student@example.com")
    response = client.post("/api/v1/auth/login", json={"email": "STUDENT@example.com", "password": PASSWORD})
    assert response.status_code == 200


def test_login_is_throttled_after_repeated_failures(client):
    _register(client)
    for _ in range(5):
        bad = client.post("/api/v1/auth/login", json={"email": "student@example.com", "password": "wrong-password"})
        assert bad.status_code == 401
    blocked = client.post("/api/v1/auth/login", json={"email": "student@example.com", "password": PASSWORD})
    assert blocked.status_code == 429
    assert int(blocked.headers["retry-after"]) > 0


def test_me_requires_a_token(client):
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "not_authenticated"
    assert response.headers["www-authenticate"] == "Bearer"


def test_me_returns_current_user(client):
    token = _register(client).json()["access_token"]
    response = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "student@example.com"


def test_garbage_and_wrongly_signed_tokens_are_rejected(client):
    now = utcnow()
    forged = jwt.encode(
        {"sub": str(uuid.uuid4()), "iat": now, "exp": now + timedelta(hours=1), "type": "access"},
        "some-other-secret-" + "y" * 32,
        algorithm="HS256",
    )
    for token in ("garbage", forged):
        response = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "invalid_token"


def test_expired_access_token_is_rejected(client, settings):
    user_id = _register(client).json()["user"]["id"]
    token, _ = create_access_token(uuid.UUID(user_id), settings, now=utcnow() - timedelta(hours=1))
    response = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_refresh_rotates_cookie_and_returns_new_access_token(client):
    _register(client)
    old_cookie = client.cookies.get(COOKIE)
    response = client.post("/api/v1/auth/refresh", headers=CSRF)
    assert response.status_code == 200
    assert response.json()["access_token"]
    assert client.cookies.get(COOKIE) != old_cookie


def test_refresh_requires_csrf_header(client):
    _register(client)
    response = client.post("/api/v1/auth/refresh")
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "csrf_failed"


def test_refresh_without_cookie_is_rejected(client):
    response = client.post("/api/v1/auth/refresh", headers=CSRF)
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_refresh_token"


def test_replay_inside_grace_window_does_not_end_the_session(app, client):
    _register(client)
    old_cookie = client.cookies.get(COOKIE)
    assert client.post("/api/v1/auth/refresh", headers=CSRF).status_code == 200
    other = TestClient(app)
    replay = other.post("/api/v1/auth/refresh", headers={**CSRF, "Cookie": f"{COOKIE}={old_cookie}"})
    assert replay.status_code == 401
    assert client.post("/api/v1/auth/refresh", headers=CSRF).status_code == 200


def test_replay_after_grace_window_revokes_the_whole_family(settings, db_engine):
    strict_app = create_app(settings.model_copy(update={"refresh_reuse_grace_seconds": 0}))
    with TestClient(strict_app) as client:
        _register(client)
        old_cookie = client.cookies.get(COOKIE)
        assert client.post("/api/v1/auth/refresh", headers=CSRF).status_code == 200
        other = TestClient(strict_app)
        replay = other.post("/api/v1/auth/refresh", headers={**CSRF, "Cookie": f"{COOKIE}={old_cookie}"})
        assert replay.status_code == 401
        assert client.post("/api/v1/auth/refresh", headers=CSRF).status_code == 401
    with db_engine.connect() as connection:
        count = connection.scalar(text("SELECT count(*) FROM audit_logs WHERE action = 'auth.refresh_reuse_detected'"))
    assert count == 1


def test_logout_revokes_the_refresh_token(app, client):
    _register(client)
    old_cookie = client.cookies.get(COOKIE)
    assert client.post("/api/v1/auth/logout").status_code == 403
    assert client.post("/api/v1/auth/logout", headers=CSRF).status_code == 204
    other = TestClient(app)
    response = other.post("/api/v1/auth/refresh", headers={**CSRF, "Cookie": f"{COOKIE}={old_cookie}"})
    assert response.status_code == 401
