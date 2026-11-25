from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import pytest
from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.engine import make_url

from app.core.config import Settings, get_settings
from app.main import create_app

BACKEND_DIR = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def test_database_url() -> str:
    base = get_settings().database_url
    if not base:
        pytest.exit("DATABASE_URL is not set. Run ./scripts/setup_db.sh first.", returncode=2)
    url = make_url(base)
    return url.set(database=f"{url.database}_test").render_as_string(hide_password=False)


@pytest.fixture(scope="session")
def settings(test_database_url: str) -> Settings:
    return Settings(
        environment="test",
        database_url=test_database_url,
        jwt_secret="test-only-secret-" + "x" * 32,
        cookie_secure=False,  # the test client speaks plain http
        argon2_time_cost=1,
        argon2_memory_kib=8192,
        argon2_parallelism=1,
        _env_file=None,
    )


@pytest.fixture(scope="session")
def db_engine(test_database_url: str) -> Iterator[Engine]:
    """Test database at migration head. Downgrade then upgrade also proves the migration is reversible."""
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", test_database_url)
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    engine = create_engine(test_database_url)
    yield engine
    engine.dispose()


@pytest.fixture(autouse=True)
def _clean_tables(db_engine: Engine) -> None:
    with db_engine.begin() as connection:
        connection.execute(text("TRUNCATE TABLE audit_logs, refresh_tokens, user_profiles, users CASCADE"))


@pytest.fixture
def app(settings: Settings) -> FastAPI:
    return create_app(settings)


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def set_role(db_engine: Engine) -> Callable[[str, str], None]:
    def _set(email: str, role: str) -> None:
        with db_engine.begin() as connection:
            connection.execute(text("UPDATE users SET role = :role WHERE email = :email"), {"role": role, "email": email})

    return _set


@pytest.fixture
def make_user(client: TestClient, set_role: Callable[[str, str], None]) -> Callable[..., dict[str, Any]]:
    def _make(email: str, role: str = "student") -> dict[str, Any]:
        response = client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "correct-horse-battery-staple", "display_name": email.split("@")[0]},
        )
        assert response.status_code == 201, response.text
        if role != "student":
            set_role(email, role)
        body = response.json()
        return {
            "id": body["user"]["id"],
            "email": email,
            "headers": {"Authorization": f"Bearer {body['access_token']}"},
        }

    return _make
