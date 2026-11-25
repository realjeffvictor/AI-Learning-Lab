import uuid

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models import Course
from app.repositories import curriculum_repository, progress_repository
from app.schemas.curriculum import (
    ConceptRead,
    CourseDetail,
    CourseSummary,
    EnrollmentRead,
    LessonDetail,
    LessonLink,
    LessonProgressRead,
    LessonSummary,
    ModuleRead,
)


def _course_summary(
    course: Course, *, modules: int, published: int, planned: int, completed: int, enrolled: bool
) -> CourseSummary:
    return CourseSummary(
        id=course.id,
        slug=course.slug,
        title=course.title,
        summary=course.summary,
        kind=course.kind,
        stage_number=course.stage_number,
        position=course.position,
        module_count=modules,
        published_lesson_count=published,
        planned_lesson_count=planned,
        completed_lesson_count=completed,
        enrolled=enrolled,
    )


def list_courses(session: Session, user_id: uuid.UUID) -> list[CourseSummary]:
    courses = curriculum_repository.list_courses(session)
    lesson_counts = curriculum_repository.lesson_counts_by_course(session)
    module_counts = curriculum_repository.module_counts_by_course(session)
    completed = curriculum_repository.completed_counts_by_course(session, user_id)
    enrolled = progress_repository.enrolled_course_ids(session, user_id)
    return [
        _course_summary(
            course,
            modules=module_counts.get(course.id, 0),
            published=lesson_counts.get(course.id, {}).get("published", 0),
            planned=lesson_counts.get(course.id, {}).get("planned", 0),
            completed=completed.get(course.id, 0),
            enrolled=course.id in enrolled,
        )
        for course in courses
    ]


def get_course(session: Session, user_id: uuid.UUID, slug: str) -> CourseDetail:
    course = curriculum_repository.get_course_by_slug(session, slug)
    if course is None:
        raise AppError(404, "course_not_found", "Course not found.")

    all_lessons = [lesson for module in course.modules for lesson in module.lessons]
    progress = progress_repository.progress_map(session, user_id, [lesson.id for lesson in all_lessons])

    modules: list[ModuleRead] = []
    for module in course.modules:
        items = [
            LessonSummary(
                id=lesson.id,
                slug=lesson.slug,
                title=lesson.title,
                summary=lesson.summary,
                position=lesson.position,
                estimated_minutes=lesson.estimated_minutes,
                status=lesson.status,
                principles=list(lesson.principles),
                progress=progress.get(lesson.id, "not_started"),
            )
            for lesson in module.lessons
        ]
        modules.append(
            ModuleRead(
                id=module.id,
                slug=module.slug,
                title=module.title,
                summary=module.summary,
                position=module.position,
                status="published" if any(item.status == "published" for item in items) else "planned",
                lessons=items,
            )
        )

    summary = _course_summary(
        course,
        modules=len(course.modules),
        published=sum(1 for lesson in all_lessons if lesson.status == "published"),
        planned=sum(1 for lesson in all_lessons if lesson.status == "planned"),
        completed=sum(1 for lesson in all_lessons if progress.get(lesson.id) == "completed"),
        enrolled=progress_repository.get_enrollment(session, user_id, course.id) is not None,
    )
    return CourseDetail(**summary.model_dump(), modules=modules)


def get_lesson(
    session: Session, user_id: uuid.UUID, course_slug: str, module_slug: str, lesson_slug: str
) -> LessonDetail:
    lesson = curriculum_repository.get_lesson(session, course_slug, module_slug, lesson_slug)
    if lesson is None:
        raise AppError(404, "lesson_not_found", "Lesson not found.")
    module = lesson.module
    course = module.course

    row = progress_repository.get_progress(session, user_id, lesson.id)
    progress = LessonProgressRead(
        status=row.status if row else "not_started",
        time_spent_seconds=row.time_spent_seconds if row else 0,
        completed_at=row.completed_at if row else None,
    )

    previous: LessonLink | None = None
    following: LessonLink | None = None
    if lesson.status == "published":
        sequence = curriculum_repository.course_lesson_sequence(session, course.id)
        ids = [item.id for item in sequence]
        index = ids.index(lesson.id)
        if index > 0:
            p = sequence[index - 1]
            previous = LessonLink(module_slug=p.module_slug, slug=p.slug, title=p.title)
        if index < len(sequence) - 1:
            n = sequence[index + 1]
            following = LessonLink(module_slug=n.module_slug, slug=n.slug, title=n.title)

    concepts = [
        ConceptRead(slug=c.slug, name=c.name, category=c.category)
        for c in curriculum_repository.lesson_concepts(session, lesson.id)
    ]
    return LessonDetail(
        id=lesson.id,
        slug=lesson.slug,
        title=lesson.title,
        summary=lesson.summary,
        estimated_minutes=lesson.estimated_minutes,
        status=lesson.status,
        objectives=list(lesson.objectives),
        principles=list(lesson.principles),
        content_md=lesson.content_md if lesson.status == "published" else None,
        concepts=concepts,
        course_slug=course.slug,
        course_title=course.title,
        module_slug=module.slug,
        module_title=module.title,
        progress=progress,
        previous=previous,
        next=following,
    )


def enroll(session: Session, user_id: uuid.UUID, course_slug: str) -> EnrollmentRead:
    course = curriculum_repository.get_course_basic(session, course_slug)
    if course is None:
        raise AppError(404, "course_not_found", "Course not found.")
    progress_repository.ensure_enrollment(session, user_id, course.id)
    session.commit()
    enrollment = progress_repository.get_enrollment(session, user_id, course.id)
    assert enrollment is not None
    return EnrollmentRead(course_slug=course.slug, enrolled_at=enrollment.created_at)
