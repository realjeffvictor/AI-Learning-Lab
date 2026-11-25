"""Load the curriculum/ folder (lessons, exercises, resources) into the database. Usage (from backend/):
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
from app.services.exercise_loader import load_exercises
from app.services.exercise_seed import seed_exercises

DEFAULT_DIR = Path(__file__).resolve().parents[2] / "curriculum"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="app.seed")
    parser.add_argument("--dir", default=str(DEFAULT_DIR), help="curriculum folder")
    parser.add_argument("--check", action="store_true", help="validate the files and stop")
    args = parser.parse_args(argv)

    try:
        root = Path(args.dir)
        data = load_curriculum(root)
        bundle = load_exercises(root, data)
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
    print(f"Exercises valid: {len(bundle.exercises)} exercises, {len(bundle.resources)} resources.")
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
            exercise_report = seed_exercises(session, bundle)
            session.commit()
    except CurriculumError as exc:
        print(f"Curriculum error: {exc}")
        return 1
    finally:
        engine.dispose()

    print(f"Created: {report.created} {exercise_report.created}")
    print(f"Updated: {report.updated} {exercise_report.updated}")
    for orphan in [*report.orphans, *exercise_report.orphans]:
        print(f"Warning: in the database but not in the files (kept): {orphan}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
