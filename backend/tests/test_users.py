import pytest
from sqlalchemy import text

CSRF = {"X-CSRF-Protection": "1"}


def test_update_own_profile(client, make_user):
    user = make_user("student@example.com")
    response = client.patch(
        "/api/v1/users/me/profile",
        json={"display_name": "  Grace Hopper ", "bio": "Compiler pioneer", "experience_level": "advanced"},
        headers=user["headers"],
    )
    assert response.status_code == 200
    profile = response.json()["profile"]
    assert profile == {"display_name": "Grace Hopper", "bio": "Compiler pioneer", "experience_level": "advanced"}
    again = client.get("/api/v1/users/me", headers=user["headers"]).json()
    assert again["profile"]["display_name"] == "Grace Hopper"


@pytest.mark.parametrize(
    "payload",
    [{"role": "admin"}, {"display_name": None}, {"experience_level": "wizard"}],
)
def test_profile_update_rejects_bad_input(client, make_user, payload):
    user = make_user("student@example.com")
    assert client.patch("/api/v1/users/me/profile", json=payload, headers=user["headers"]).status_code == 422


def test_list_users_requires_authentication(client):
    assert client.get("/api/v1/users").status_code == 401


@pytest.mark.parametrize(("role", "expected"), [("student", 403), ("instructor", 403), ("admin", 200)])
def test_list_users_is_admin_only(client, make_user, role, expected):
    actor = make_user(f"{role}@example.com", role)
    assert client.get("/api/v1/users", headers=actor["headers"]).status_code == expected


def test_list_users_returns_paginated_items(client, make_user):
    admin = make_user("admin@example.com", "admin")
    make_user("one@example.com")
    make_user("two@example.com")
    body = client.get("/api/v1/users?page=1&page_size=2", headers=admin["headers"]).json()
    assert body["total"] == 3 and body["page_size"] == 2 and len(body["items"]) == 2
    assert all("password" not in item for item in body["items"])


def test_list_users_rejects_oversized_page(client, make_user):
    admin = make_user("admin@example.com", "admin")
    assert client.get("/api/v1/users?page_size=1000", headers=admin["headers"]).status_code == 422


@pytest.mark.parametrize(("role", "expected"), [("student", 403), ("instructor", 403), ("admin", 200)])
def test_update_user_is_admin_only(client, make_user, role, expected):
    target = make_user("target@example.com")
    actor = make_user(f"{role}@example.com", role)
    response = client.patch(f"/api/v1/users/{target['id']}", json={"role": "instructor"}, headers=actor["headers"])
    assert response.status_code == expected


def test_role_change_is_audited(client, make_user, db_engine):
    admin = make_user("admin@example.com", "admin")
    target = make_user("target@example.com")
    client.patch(f"/api/v1/users/{target['id']}", json={"role": "instructor"}, headers=admin["headers"])
    with db_engine.connect() as connection:
        row = connection.execute(
            text("SELECT details FROM audit_logs WHERE action = 'user.role_changed'")
        ).one()
    assert row.details["to"] == "instructor" and row.details["from"] == "student"


def test_admin_cannot_modify_self(client, make_user):
    admin = make_user("admin@example.com", "admin")
    response = client.patch(f"/api/v1/users/{admin['id']}", json={"role": "student"}, headers=admin["headers"])
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "cannot_modify_self"


def test_update_unknown_user_is_404(client, make_user):
    admin = make_user("admin@example.com", "admin")
    response = client.patch(
        "/api/v1/users/00000000-0000-4000-8000-000000000000", json={"is_active": False}, headers=admin["headers"]
    )
    assert response.status_code == 404


def test_deactivated_user_loses_access_immediately(client, make_user):
    admin = make_user("admin@example.com", "admin")
    target = make_user("learner@example.com")  # the client cookie jar now holds the learner's refresh cookie
    response = client.patch(f"/api/v1/users/{target['id']}", json={"is_active": False}, headers=admin["headers"])
    assert response.status_code == 200

    me = client.get("/api/v1/users/me", headers=target["headers"])
    assert me.status_code == 403 and me.json()["error"]["code"] == "account_disabled"
    assert client.post("/api/v1/auth/refresh", headers=CSRF).status_code == 401
    login = client.post(
        "/api/v1/auth/login", json={"email": "learner@example.com", "password": "correct-horse-battery-staple"}
    )
    assert login.status_code == 403 and login.json()["error"]["code"] == "account_disabled"
