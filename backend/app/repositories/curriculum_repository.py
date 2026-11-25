import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import Concept, Course, Lesson, LessonConcept, LessonProgress, Module


def list_courses(session: Session) -> list[Course]:
    return list(session.scalars(select(Course).order_by(Course.position, Course.slug)))


def lesson_counts_by_course(session: Session) -> dict[uuid.UUID, dict[str, int]]:
    rows = session.execute(
        select(Module.course_id, Lesson.status, func.count(Lesson.id))
        .select_from(Module)
        .join(Lesson, Lesson.module_id == Module.id)
        .group_by(Module.course_id, Lesson.status)
    ).all()
    result: dict[uuid.UUID, dict[str, int]] = {}
    for course_id, status, count in rows:
        result.setdefault(course_id, {})[status] = count
    return result


def module_counts_by_course(session: Session) -> dict[uuid.UUID, int]:
    rows = session.execute(select(Module.course_id, func.count(Module.id)).group_by(Module.course_id)).all()
    return {course_id: count for course_id, count in rows}


def completed_counts_by_course(session: Session, user_id: uuid.UUID) -> dict[uuid.UUID, int]:
    rows = session.execute(
        select(Module.course_id, func.count(LessonProgress.id))
        .select_from(LessonProgress)
        .join(Lesson, Lesson.id == LessonProgress.lesson_id)
        .join(Module, Module.id == Lesson.module_id)
        .where(LessonProgress.user_id == user_id, LessonProgress.status == "completed")
        .group_by(Module.course_id)
    ).all()
    return {course_id: count for course_id, count in rows}


def get_course_basic(session: Session, slug: str) -> Course | None:
    return session.scalar(select(Course).where(Course.slug == slug))


def get_course_by_slug(session: Session, slug: str) -> Course | None:
    return session.scalar(
        select(Course)
        .where(Course.slug == slug)
        .options(selectinload(Course.modules).selectinload(Module.lessons))
    )


def get_module(session: Session, module_id: uuid.UUID) -> Module | None:
    return session.get(Module, module_id)


def get_lesson_by_id(session: Session, lesson_id: uuid.UUID) -> Lesson | None:
    return session.get(Lesson, lesson_id)


def get_lesson(session: Session, course_slug: str, module_slug: str, lesson_slug: str) -> Lesson | None:
    return session.scalar(
        select(Lesson)
        .join(Module, Module.id == Lesson.module_id)
        .join(Course, Course.id == Module.course_id)
        .where(Course.slug == course_slug, Module.slug == module_slug, Lesson.slug == lesson_slug)
        .options(selectinload(Lesson.module).selectinload(Module.course))
    )


def lesson_concepts(session: Session, lesson_id: uuid.UUID) -> list[Concept]:
    return list(
        session.scalars(
            select(Concept)
            .join(LessonConcept, LessonConcept.concept_id == Concept.id)
            .where(LessonConcept.lesson_id == lesson_id)
            .order_by(Concept.category, Concept.name)
        )
    )


def lesson_concept_ids(session: Session, lesson_id: uuid.UUID) -> list[uuid.UUID]:
    return list(session.scalars(select(LessonConcept.concept_id).where(LessonConcept.lesson_id == lesson_id)))


def course_lesson_sequence(session: Session, course_id: uuid.UUID):
    """Published lessons of a course in reading order."""
    return session.execute(
        select(Lesson.id, Lesson.slug, Lesson.title, Module.slug.label("module_slug"))
        .select_from(Lesson)
        .join(Module, Module.id == Lesson.module_id)
        .where(Module.course_id == course_id, Lesson.status == "published")
        .order_by(Module.position, Lesson.position)
    ).all()
