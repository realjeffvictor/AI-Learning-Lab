"""Load the curriculum/ folder into the database. Usage (from backend/):
    .venv/bin/python -m app.seed            validate, then write (safe to re-run)
    .venv/bin/python -m app.seed --check    validate only, no database needed
"""
import argparse
import sys
from pathlib import Path

from app.core.config import get_settings
from app.core.database import create_db_engine, create_session_factory
from app.services.curriculum_loader import CurriculumError, load_curriculum
from app.services.curriculum_seed import seed_curriculum

DEFAULT_DIR = Path(__file__).resolve().parents[2] / "curriculum"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="app.seed")
    parser.add_argument("--dir", default=str(DEFAULT_DIR), help="curriculum folder")
    parser.add_argument("--check", action="store_true", help="validate the files and stop")
    args = parser.parse_args(argv)

    try:
        data = load_curriculum(Path(args.dir))
    except CurriculumError as exc:
        print(f"Curriculum error: {exc}")
        return 1

    lessons = [lesson for course in data.courses for module in course.modules for lesson in module.lessons]
    published = sum(1 for lesson in lessons if lesson.content_md)
    print(
        f"Curriculum valid: {len(data.concepts)} concepts, {len(data.courses)} courses, "
        f"{sum(len(c.modules) for c in data.courses)} modules, {len(lessons)} lessons "
        f"({published} written, {len(lessons) - published} planned)."
    )
    if args.check:
        return 0

    settings = get_settings()
    if not settings.database_url:
        print("DATABASE_URL is not set. Run ./scripts/setup_db.sh first.")
        return 1
    engine = create_db_engine(settings.database_url)
    try:
        with create_session_factory(engine)() as session:
            report = seed_curriculum(session, data)
            session.commit()
    finally:
        engine.dispose()

    print(f"Created: {report.created}")
    print(f"Updated: {report.updated}")
    for orphan in report.orphans:
        print(f"Warning: in the database but not in the files (kept): {orphan}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
