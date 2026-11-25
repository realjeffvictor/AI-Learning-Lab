import logging
from datetime import datetime, timezone
from typing import Literal

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings
from app.schemas.health import HealthResponse

logger = logging.getLogger("app.health")


def check_database(session_factory: sessionmaker[Session] | None) -> Literal["ok", "unavailable", "not_configured"]:
    if session_factory is None:
        return "not_configured"
    try:
        with session_factory() as session:
            session.execute(text("SELECT 1"))
        return "ok"
    except SQLAlchemyError:
        logger.warning("database_health_check_failed")
        return "unavailable"


def get_health(settings: Settings, session_factory: sessionmaker[Session] | None) -> HealthResponse:
    """Liveness plus database connectivity. The API stays 'ok' when the database is down so it can report why."""
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
        database=check_database(session_factory),
        timestamp=datetime.now(timezone.utc),
    )
