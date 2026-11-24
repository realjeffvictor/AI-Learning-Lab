from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


def _app():
    return create_app(Settings(environment="test", _env_file=None))


def test_unknown_route_uses_error_envelope(client):
    response = client.get("/api/v1/nope")
    assert response.status_code == 404
    error = response.json()["error"]
    assert error["code"] == "not_found"
    assert error["request_id"]


def test_validation_error_uses_error_envelope():
    app = _app()

    @app.get("/items/{item_id}")
    def read_item(item_id: int):
        return {"id": item_id}

    response = TestClient(app).get("/items/abc")
    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "validation_error"
    assert error["details"]


def test_unhandled_exception_hides_internals():
    app = _app()

    @app.get("/boom")
    def boom():
        raise RuntimeError("secret internal detail")

    response = TestClient(app, raise_server_exceptions=False).get("/boom")
    assert response.status_code == 500
    assert response.json()["error"]["code"] == "internal_error"
    assert "secret" not in response.text


def test_docs_disabled_in_production():
    app = create_app(Settings(environment="production", _env_file=None))
    assert TestClient(app).get("/docs").status_code == 404


def test_cors_allows_configured_origin(client):
    response = client.options(
        "/api/v1/health",
        headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "GET"},
    )
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_cors_rejects_unknown_origin(client):
    response = client.options(
        "/api/v1/health",
        headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "GET"},
    )
    assert "access-control-allow-origin" not in response.headers
