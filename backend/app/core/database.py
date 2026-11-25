from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker


def create_db_engine(database_url: str) -> Engine:
    """Small pool on purpose: the target machines have little RAM, and PostgreSQL max_connections is low."""
    return create_engine(database_url, pool_size=4, max_overflow=4, pool_pre_ping=True)


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False)
