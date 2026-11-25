import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.models import Concept, Course, Enrollment, Lesson, LessonProgress, Module, UserCompetency


def progress_map(session: Session, user_id: uuid.UUID, lesson_ids: list[uuid.UUID]) -> dict[uuid.UUID, str]:
    if not lesson_ids:
        return {}
    rows = session.execute(
        select(LessonProgress.lesson_id, LessonProgress.status).where(
            LessonProgress.user_id == user_id, LessonProgress.lesson_id.in_(lesson_ids)
        )
    ).all()
    return {lesson_id: status for lesson_id, status in rows}


def get_progress(
    session: Session, user_id: uuid.UUID, lesson_id: uuid.UUID, for_update: bool = False
) -> LessonProgress | None:
    statement = select(LessonProgress).where(LessonProgress.user_id == user_id, LessonProgress.lesson_id == lesson_id)
    if for_update:
        statement = statement.with_for_update().execution_options(populate_existing=True)
    return session.scalar(statement)


def ensure_progress(session: Session, user_id: uuid.UUID, lesson_id: uuid.UUID, now: datetime) -> None:
    session.execute(
        pg_insert(LessonProgress)
        .values(
            id=uuid.uuid4(),
            user_id=user_id,
            lesson_id=lesson_id,
            status="in_progress",
            time_spent_seconds=0,
            started_at=now,
            last_visited_at=now,
        )
        .on_conflict_do_nothing(index_elements=["user_id", "lesson_id"])
    )


def ensure_enrollment(session: Session, user_id: uuid.UUID, course_id: uuid.UUID) -> None:
    session.execute(
        pg_insert(Enrollment)
        .values(id=uuid.uuid4(), user_id=user_id, course_id=course_id)
        .on_conflict_do_nothing(index_elements=["user_id", "course_id"])
    )


def get_enrollment(session: Session, user_id: uuid.UUID, course_id: uuid.UUID) -> Enrollment | None:
    return session.scalar(select(Enrollment).where(Enrollment.user_id == user_id, Enrollment.course_id == course_id))


def enrolled_course_ids(session: Session, user_id: uuid.UUID) -> set[uuid.UUID]:
    return set(session.scalars(select(Enrollment.course_id).where(Enrollment.user_id == user_id)))


def add_competency_evidence(session: Session, user_id: uuid.UUID, concept_ids: list[uuid.UUID]) -> None:
    if not concept_ids:
        return
    table = UserCompetency.__table__
    statement = pg_insert(UserCompetency).values(
        [{"user_id": user_id, "concept_id": concept_id, "lessons_completed": 1} for concept_id in concept_ids]
    )
    session.execute(
        statement.on_conflict_do_update(
            index_elements=["user_id", "concept_id"],
            set_={"lessons_completed": table.c.lessons_completed + 1, "updated_at": func.now()},
        )
    )


def total_time_seconds(session: Session, user_id: uuid.UUID) -> int:
    total = session.scalar(
        select(func.coalesce(func.sum(LessonProgress.time_spent_seconds), 0)).where(LessonProgress.user_id == user_id)
    )
    return int(total or 0)


def completed_lesson_total(session: Session, user_id: uuid.UUID) -> int:
    return int(
        session.scalar(
            select(func.count(LessonProgress.id)).where(
                LessonProgress.user_id == user_id, LessonProgress.status == "completed"
            )
        )
        or 0
    )


def competencies(session: Session, user_id: uuid.UUID):
    return session.execute(
        select(Concept.slug, Concept.name, Concept.category, UserCompetency.lessons_completed)
        .select_from(UserCompetency)
        .join(Concept, Concept.id == UserCompetency.concept_id)
        .where(UserCompetency.user_id == user_id)
        .order_by(Concept.category, Concept.name)
    ).all()


def _lesson_columns():
    return (
        Lesson.title.label("lesson_title"),
        Lesson.slug.label("lesson_slug"),
        Module.slug.label("module_slug"),
        Course.slug.label("course_slug"),
        Course.title.label("course_title"),
    )


def in_progress_lesson(session: Session, user_id: uuid.UUID):
    return session.execute(
        select(*_lesson_columns())
        .select_from(LessonProgress)
        .join(Lesson, Lesson.id == LessonProgress.lesson_id)
        .join(Module, Module.id == Lesson.module_id)
        .join(Course, Course.id == Module.course_id)
        .where(
            LessonProgress.user_id == user_id,
            LessonProgress.status == "in_progress",
            Lesson.status == "published",
        )
        .order_by(LessonProgress.last_visited_at.desc())
        .limit(1)
    ).first()


def next_unfinished_lesson(session: Session, user_id: uuid.UUID):
    completed = select(LessonProgress.id).where(
        LessonProgress.user_id == user_id,
        LessonProgress.lesson_id == Lesson.id,
        LessonProgress.status == "completed",
    )
    return session.execute(
        select(*_lesson_columns())
        .select_from(Lesson)
        .join(Module, Module.id == Lesson.module_id)
        .join(Course, Course.id == Module.course_id)
        .where(Lesson.status == "published", ~completed.exists())
        .order_by(Course.position, Module.position, Lesson.position)
        .limit(1)
    ).first()
