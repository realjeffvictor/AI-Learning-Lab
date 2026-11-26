"""Walks every API route. A new endpoint that is reachable without a token, or open to the wrong role,
fails here until it is either protected or consciously added to PUBLIC."""
import re
import uuid

import pytest
from fastapi.routing import APIRoute

from app.main import app as main_app

PUBLIC = {
    ("GET", "/api/v1/health"),
    ("POST", "/api/v1/auth/register"),
    ("POST", "/api/v1/auth/login"),
    ("POST", "/api/v1/auth/refresh"),
    ("POST", "/api/v1/auth/logout"),
    ("GET", "/api/v1/certificates/verify/{code}"),
}
ADMIN_ONLY = [("GET", "/api/v1/users"), ("PATCH", "/api/v1/users/{user_id}")]


def _routes():
    found = []
    for route in main_app.routes:
        if isinstance(route, APIRoute) and route.path.startswith("/api/v1"):
            for method in sorted(route.methods - {"HEAD", "OPTIONS"}):
                found.append((method, route.path))
    return found


ROUTES = _routes()
PROTECTED = [r for r in ROUTES if r not in PUBLIC]
STAFF = [r for r in ROUTES if r[1].startswith(("/api/v1/manage", "/api/v1/reviews"))]


def _fill(path: str) -> str:
    return re.sub(r"\{([^}]+)\}", lambda m: str(uuid.uuid4()) if m.group(1).endswith("_id") else "x", path)


def _ids(routes):
    return [f"{method} {path}" for method, path in routes]


def test_the_public_list_matches_reality():
    assert PUBLIC <= set(ROUTES), "PUBLIC contains a route that no longer exists"
    assert len(ROUTES) > 40


@pytest.mark.parametrize(("method", "path"), PROTECTED, ids=_ids(PROTECTED))
def test_every_other_route_requires_a_token(client, method, path):
    response = client.request(method, _fill(path))
    assert response.status_code == 401, f"{method} {path} answered {response.status_code} without a token"


@pytest.mark.parametrize(("method", "path"), STAFF, ids=_ids(STAFF))
def test_students_cannot_use_staff_routes(client, make_user, method, path):
    student = make_user("student@example.com")
    response = client.request(method, _fill(path), headers=student["headers"])
    assert response.status_code == 403, f"{method} {path} answered {response.status_code} for a student"


@pytest.mark.parametrize("role", ["student", "instructor"])
@pytest.mark.parametrize(("method", "path"), ADMIN_ONLY, ids=_ids(ADMIN_ONLY))
def test_only_admins_can_use_admin_routes(client, make_user, role, method, path):
    user = make_user(f"{role}@example.com", role)
    response = client.request(method, _fill(path), headers=user["headers"])
    assert response.status_code == 403
