import json
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
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.main import create_app
from app.services.curriculum_loader import load_curriculum
from app.services.curriculum_seed import SeedReport, seed_curriculum

BACKEND_DIR = Path(__file__).resolve().parents[1]

SAMPLE_CONCEPTS = [
    {"slug": "logic", "name": "Logic", "category": "A", "description": "Reasoning step by step."},
    {"slug": "loops", "name": "Loops", "category": "A", "description": "Repeating work."},
    {"slug": "prompting", "name": "Prompting", "category": "B", "description": "Directing AI."},
]

SAMPLE_ALPHA = {
    "slug": "alpha",
    "title": "Alpha",
    "summary": "First stage",
    "kind": "stage",
    "stage_number": 1,
    "modules": [
        {
            "slug": "intro",
            "title": "Intro",
            "summary": "Start here",
            "lessons": [
                {"slug": "one", "title": "One", "summary": "First", "minutes": 5, "principles": ["U"],
                 "concepts": ["logic", "loops"], "objectives": ["Do a thing"]},
                {"slug": "two", "title": "Two", "summary": "Second", "minutes": 6, "principles": ["U", "V"],
                 "concepts": ["logic"], "objectives": []},
                {"slug": "three", "title": "Three"},
            ],
        },
        {"slug": "empty", "title": "Empty", "lessons": []},
    ],
}

SAMPLE_BETA = {"slug": "beta", "title": "Beta", "summary": "A track", "kind": "track", "modules": []}


def write_sample_curriculum(root: Path) -> None:
    (root / "concepts.json").write_text(json.dumps(SAMPLE_CONCEPTS))
    alpha = root / "courses" / "01-alpha"
    (alpha / "intro").mkdir(parents=True)
    (alpha / "course.json").write_text(json.dumps(SAMPLE_ALPHA))
    (alpha / "intro" / "one.md").write_text("## One\n\nFirst lesson body.\n")
    (alpha / "intro" / "two.md").write_text("## Two\n\nSecond lesson body.\n")
    beta = root / "courses" / "02-beta"
    beta.mkdir(parents=True)
    (beta / "course.json").write_text(json.dumps(SAMPLE_BETA))


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
    """Test database at migration head. Downgrade then upgrade also proves the migrations are reversible."""
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", test_database_url)
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    engine = create_engine(test_database_url)
    yield engine
    engine.dispose()


@pytest.fixture(autouse=True)
def _clean_tables(db_engine: Engine) -> None:
    # CASCADE also empties enrollments, progress, competencies, modules, lessons and lesson_concepts.
    with db_engine.begin() as connection:
        connection.execute(
            text("TRUNCATE TABLE audit_logs, refresh_tokens, user_profiles, users, courses, concepts CASCADE")
        )


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


@pytest.fixture
def curriculum_root(tmp_path: Path) -> Path:
    write_sample_curriculum(tmp_path)
    return tmp_path


@pytest.fixture
def seed(db_engine: Engine, curriculum_root: Path) -> Callable[[], SeedReport]:
    def _run() -> SeedReport:
        data = load_curriculum(curriculum_root)
        with Session(db_engine) as session:
            report = seed_curriculum(session, data)
            session.commit()
        return report

    return _run
