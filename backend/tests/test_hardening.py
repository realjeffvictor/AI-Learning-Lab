import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


def test_security_headers_are_on_every_kind_of_response(client):
    ok = client.get("/api/v1/health")
    assert ok.headers["x-content-type-options"] == "nosniff"
    assert ok.headers["x-frame-options"] == "DENY"
    assert ok.headers["referrer-policy"] == "no-referrer"
    assert "geolocation=()" in ok.headers["permissions-policy"]
    assert "strict-transport-security" not in ok.headers
    assert client.get("/api/v1/nope").headers["x-content-type-options"] == "nosniff"
    preflight = client.options(
        "/api/v1/health", headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "GET"}
    )
    assert preflight.headers["x-frame-options"] == "DENY"


def test_production_adds_hsts_and_a_strict_csp(settings):
    app = create_app(settings.model_copy(update={"environment": "production"}))
    with TestClient(app) as client:
        response = client.get("/api/v1/health")
    assert "max-age=" in response.headers["strict-transport-security"]
    assert "default-src 'none'" in response.headers["content-security-policy"]


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        ("postgres://u:p@h:5432/db", "postgresql+psycopg://u:p@h:5432/db"),
        ("postgresql://u:p@h/db", "postgresql+psycopg://u:p@h/db"),
        ("postgresql+psycopg://u:p@h/db", "postgresql+psycopg://u:p@h/db"),
        ("", ""),
    ],
)
def test_database_url_is_normalised(given, expected):
    assert Settings(database_url=given, _env_file=None).database_url == expected


def _production(**overrides) -> Settings:
    values = dict(
        environment="production",
        jwt_secret="s" * 40,
        database_url="postgresql+psycopg://u:p@h/db",
        cookie_secure=True,
        cors_origins="https://app.example.com",
    )
    values.update(overrides)
    return Settings(_env_file=None, **values)


def test_a_correct_production_config_starts():
    _production().assert_production_ready()


@pytest.mark.parametrize(
    ("override", "message"),
    [
        ({"jwt_secret": "short"}, "JWT_SECRET"),
        ({"database_url": ""}, "DATABASE_URL"),
        ({"cookie_secure": False}, "COOKIE_SECURE"),
        ({"cors_origins": "http://localhost:5173"}, "https://"),
        ({"cors_origins": "https://ok.example.com,http://evil.example.com"}, "https://"),
    ],
)
def test_unsafe_production_configs_refuse_to_start(override, message):
    with pytest.raises(RuntimeError, match=message):
        _production(**override).assert_production_ready()


def test_development_config_is_not_checked():
    Settings(environment="development", cors_origins="http://localhost:5173", _env_file=None).assert_production_ready()
