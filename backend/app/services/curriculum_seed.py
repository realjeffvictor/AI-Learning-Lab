"""Writes validated curriculum data into the database. Safe to run repeatedly."""
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models import Concept, Course, Lesson, LessonConcept, Module
from app.services.curriculum_loader import CurriculumData


def _zero() -> dict[str, int]:
    return {"concepts": 0, "courses": 0, "modules": 0, "lessons": 0}


@dataclass
class SeedReport:
    created: dict[str, int] = field(default_factory=_zero)
    updated: dict[str, int] = field(default_factory=_zero)
    orphans: list[str] = field(default_factory=list)


def _apply(obj: Any, values: dict[str, Any]) -> bool:
    changed = False
    for key, value in values.items():
        if getattr(obj, key) != value:
            setattr(obj, key, value)
            changed = True
    return changed


def _upsert(
    session: Session,
    report: SeedReport,
    key: str,
    existing: Any,
    model: type,
    identity: dict[str, Any],
    values: dict[str, Any],
) -> tuple[Any, str]:
    if existing is None:
        obj = model(**identity, **values)
        session.add(obj)
        report.created[key] += 1
        return obj, "created"
    if _apply(existing, values):
        report.updated[key] += 1
        return existing, "updated"
    return existing, "same"


def seed_curriculum(session: Session, data: CurriculumData) -> SeedReport:
    """Upsert by slug. Nothing is ever deleted: content missing from the files is reported as an orphan,
    because learners may have progress attached to it."""
    report = SeedReport()

    concepts = {c.slug: c for c in session.scalars(select(Concept))}
    for item in data.concepts:
        obj, _ = _upsert(
            session, report, "concepts", concepts.get(item.slug), Concept, {"slug": item.slug},
            {"name": item.name, "category": item.category, "description": item.description},
        )
        concepts[item.slug] = obj
    session.flush()

    existing_courses = {c.slug: c for c in session.scalars(select(Course))}
    for course_position, course in enumerate(data.courses, start=1):
        course_obj, _ = _upsert(
            session, report, "courses", existing_courses.get(course.slug), Course, {"slug": course.slug},
            {
                "title": course.title,
                "summary": course.summary,
                "kind": course.kind,
                "stage_number": course.stage_number,
                "position": course_position,
            },
        )
        session.flush()

        existing_modules = {m.slug: m for m in session.scalars(select(Module).where(Module.course_id == course_obj.id))}
        for module_position, module in enumerate(course.modules, start=1):
            module_obj, _ = _upsert(
                session, report, "modules", existing_modules.get(module.slug), Module,
                {"course_id": course_obj.id, "slug": module.slug},
                {"title": module.title, "summary": module.summary, "position": module_position},
            )
            session.flush()

            existing_lessons = {
                l.slug: l for l in session.scalars(select(Lesson).where(Lesson.module_id == module_obj.id))
            }
            for lesson_position, lesson in enumerate(module.lessons, start=1):
                lesson_obj, state = _upsert(
                    session, report, "lessons", existing_lessons.get(lesson.slug), Lesson,
                    {"module_id": module_obj.id, "slug": lesson.slug},
                    {
                        "title": lesson.title,
                        "summary": lesson.summary,
                        "position": lesson_position,
                        "estimated_minutes": lesson.minutes,
                        "status": "published" if lesson.content_md else "planned",
                        "content_md": lesson.content_md,
                        "objectives": list(lesson.objectives),
                        "principles": list(lesson.principles),
                    },
                )
                session.flush()

                wanted = {concepts[slug].id for slug in lesson.concepts}
                current = set(
                    session.scalars(select(LessonConcept.concept_id).where(LessonConcept.lesson_id == lesson_obj.id))
                )
                for concept_id in wanted - current:
                    session.add(LessonConcept(lesson_id=lesson_obj.id, concept_id=concept_id))
                stale = current - wanted
                if stale:
                    session.execute(
                        delete(LessonConcept).where(
                            LessonConcept.lesson_id == lesson_obj.id, LessonConcept.concept_id.in_(stale)
                        )
                    )
                if wanted != current and state == "same":
                    report.updated["lessons"] += 1
    session.flush()

    wanted_courses = {c.slug for c in data.courses}
    wanted_modules = {(c.slug, m.slug) for c in data.courses for m in c.modules}
    wanted_lessons = {(c.slug, m.slug, l.slug) for c in data.courses for m in c.modules for l in m.lessons}

    for (slug,) in session.execute(select(Course.slug)).all():
        if slug not in wanted_courses:
            report.orphans.append(f"course {slug}")
    module_rows = session.execute(
        select(Course.slug, Module.slug).select_from(Module).join(Course, Course.id == Module.course_id)
    ).all()
    for course_slug, module_slug in module_rows:
        if (course_slug, module_slug) not in wanted_modules:
            report.orphans.append(f"module {course_slug}/{module_slug}")
    lesson_rows = session.execute(
        select(Course.slug, Module.slug, Lesson.slug)
        .select_from(Lesson)
        .join(Module, Module.id == Lesson.module_id)
        .join(Course, Course.id == Module.course_id)
    ).all()
    for course_slug, module_slug, lesson_slug in lesson_rows:
        if (course_slug, module_slug, lesson_slug) not in wanted_lessons:
            report.orphans.append(f"lesson {course_slug}/{module_slug}/{lesson_slug}")
    return report
