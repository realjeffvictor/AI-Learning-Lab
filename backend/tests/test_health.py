from datetime import datetime


def test_health_returns_ok(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["environment"] == "test"
    assert body["service"] == "AI Learning Lab API"
    datetime.fromisoformat(body["timestamp"])


def test_health_sets_request_id_header(client):
    response = client.get("/api/v1/health")
    assert len(response.headers["x-request-id"]) >= 8


def test_valid_client_request_id_is_echoed(client):
    response = client.get("/api/v1/health", headers={"X-Request-ID": "trace-12345678"})
    assert response.headers["x-request-id"] == "trace-12345678"


def test_unsafe_client_request_id_is_replaced(client):
    response = client.get("/api/v1/health", headers={"X-Request-ID": "bad id!"})
    assert response.headers["x-request-id"] != "bad id!"
