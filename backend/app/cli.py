"""Administrative commands. Usage (from backend/):
    .venv/bin/python -m app.cli create-admin --email you@example.com --display-name "Your Name"
"""
import argparse
import getpass
import sys

from email_validator import EmailNotValidError, validate_email

from app.core.config import get_settings
from app.core.database import create_db_engine, create_session_factory
from app.core.security import PasswordService, check_password_policy
from app.repositories import audit_repository, user_repository
from app.services import user_service


def create_admin(email_input: str, display_name: str) -> int:
    settings = get_settings()
    if not settings.database_url:
        print("DATABASE_URL is not set. Run ./scripts/setup_db.sh first.")
        return 1
    try:
        email = validate_email(email_input, check_deliverability=False).normalized.lower()
    except EmailNotValidError as exc:
        print(f"Invalid email: {exc}")
        return 1

    engine = create_db_engine(settings.database_url)
    try:
        with create_session_factory(engine)() as session:
            existing = user_repository.get_by_email(session, email)
            if existing:
                if existing.role == "admin":
                    print(f"{email} is already an admin.")
                    return 0
                existing.role = "admin"
                audit_repository.record(session, "admin.promoted_via_cli", actor_user_id=existing.id)
                session.commit()
                print(f"Existing user {email} promoted to admin.")
                return 0

            password = getpass.getpass("Password: ")
            if password != getpass.getpass("Confirm password: "):
                print("Passwords do not match.")
                return 1
            problem = check_password_policy(password, email)
            if problem:
                print(problem)
                return 1
            user = user_service.create_user(
                session,
                PasswordService.from_settings(settings),
                email=email,
                password=password,
                display_name=display_name,
                role="admin",
            )
            audit_repository.record(session, "admin.created_via_cli", actor_user_id=user.id)
            session.commit()
            print(f"Admin {email} created.")
            return 0
    finally:
        engine.dispose()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="app.cli")
    commands = parser.add_subparsers(dest="command", required=True)
    admin = commands.add_parser("create-admin", help="Create an admin, or promote an existing user.")
    admin.add_argument("--email", required=True)
    admin.add_argument("--display-name", required=True)
    args = parser.parse_args(argv)
    return create_admin(args.email, args.display_name.strip())


if __name__ == "__main__":
    sys.exit(main())
