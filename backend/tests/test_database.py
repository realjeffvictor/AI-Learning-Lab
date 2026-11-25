import pytest
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError


def test_expected_tables_exist(db_engine):
    names = set(inspect(db_engine).get_table_names())
    assert {"users", "user_profiles", "refresh_tokens", "audit_logs", "alembic_version"} <= names


def test_role_check_constraint_rejects_unknown_role(db_engine):
    with pytest.raises(IntegrityError), db_engine.begin() as connection:
        connection.execute(
            text("INSERT INTO users (id, email, password_hash, role) VALUES (gen_random_uuid(), 'a@example.com', 'x', 'root')")
        )


def test_email_must_be_lowercase_in_the_database(db_engine):
    with pytest.raises(IntegrityError), db_engine.begin() as connection:
        connection.execute(
            text("INSERT INTO users (id, email, password_hash) VALUES (gen_random_uuid(), 'Mixed@Example.com', 'x')")
        )


def test_server_defaults_apply(db_engine):
    with db_engine.begin() as connection:
        connection.execute(
            text("INSERT INTO users (id, email, password_hash) VALUES (gen_random_uuid(), 'd@example.com', 'x')")
        )
        row = connection.execute(text("SELECT role, is_active, created_at FROM users")).one()
    assert row.role == "student" and row.is_active is True and row.created_at is not None


def test_deleting_a_user_cascades_to_profile_and_tokens(client, db_engine):
    client.post(
        "/api/v1/auth/register",
        json={"email": "gone@example.com", "password": "correct-horse-battery-staple", "display_name": "Gone"},
    )
    with db_engine.begin() as connection:
        connection.execute(text("DELETE FROM users"))
        assert connection.scalar(text("SELECT count(*) FROM user_profiles")) == 0
        assert connection.scalar(text("SELECT count(*) FROM refresh_tokens")) == 0
