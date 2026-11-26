import uuid
from collections import defaultdict
from typing import Any

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models import Concept, Exercise, Lesson, User
from app.repositories import (
    audit_repository,
    content_repository,
    curriculum_repository,
    exercise_repository,
    project_repository,
)
from app.schemas.manage import (
    ConceptOption,
    ContentCourse,
    ContentLesson,
    ContentModule,
    ContentProject,
    ContentTree,
    ExerciseCreate,
    ExerciseEdit,
    ExerciseWrite,
    LessonCreate,
    LessonEdit,
    LessonWrite,
    ProjectEdit,
    ProjectWrite,
)
from app.schemas.project import Requirement
from app.services.curriculum_loader import SLUG_PATTERN, CurriculumError
from app.services.exercise_loader import IDENT, _code, _puzzle, _quiz


def _audit(session: Session, actor: User, action: str, ip: str | None, **details: str) -> None:
    audit_repository.record(session, action, actor_user_id=actor.id, ip_address=ip, details=details)


def _concepts(session: Session, slugs: list[str]) -> dict[str, Concept]:
    found = content_repository.concepts_by_slugs(session, slugs)
    missing = [slug for slug in slugs if slug not in found]
    if missing:
        raise AppError(422, "unknown_concept", f"Unknown concept: {', '.join(missing)}.")
    return found


# ------------------------------------------------------------------ overview of content
def get_tree(session: Session) -> ContentTree:
    counts = content_repository.exercise_counts(session)
    projects_by_course: dict[uuid.UUID, list[ContentProject]] = defaultdict(list)
    for project, course in project_repository.list_projects(session):
        projects_by_course[course.id].append(
            ContentProject(
                id=project.id, slug=project.slug, title=project.title, kind=project.kind,
                managed_in_app=project.managed_in_app,
            )
        )
    courses = [
        ContentCourse(
            id=course.id,
            slug=course.slug,
            title=course.title,
            kind=course.kind,
            modules=[
                ContentModule(
                    id=module.id,
                    slug=module.slug,
                    title=module.title,
                    lessons=[
                        ContentLesson(
                            id=lesson.id, slug=lesson.slug, title=lesson.title, status=lesson.status,
                            managed_in_app=lesson.managed_in_app, exercise_count=counts.get(lesson.id, 0),
                        )
                        for lesson in module.lessons
                    ],
                )
                for module in course.modules
            ],
            projects=projects_by_course.get(course.id, []),
        )
        for course in content_repository.tree(session)
    ]
    return ContentTree(courses=courses)


def list_concepts(session: Session) -> list[ConceptOption]:
    return [ConceptOption(slug=c.slug, name=c.name, category=c.category) for c in content_repository.all_concepts(session)]


# ------------------------------------------------------------------ lessons
def _lesson_edit(session: Session, lesson: Lesson) -> LessonEdit:
    module = lesson.module
    course = module.course
    return LessonEdit(
        id=lesson.id,
        slug=lesson.slug,
        title=lesson.title,
        summary=lesson.summary,
        minutes=lesson.estimated_minutes,
        status=lesson.status,
        objectives=list(lesson.objectives),
        principles=list(lesson.principles),
        concepts=content_repository.lesson_concept_slugs(session, lesson.id),
        content_md=lesson.content_md,
        module_id=module.id,
        module_slug=module.slug,
        module_title=module.title,
        course_slug=course.slug,
        course_title=course.title,
        managed_in_app=lesson.managed_in_app,
    )


def _content(value: str | None) -> str | None:
    cleaned = (value or "").strip()
    return cleaned or None


def get_lesson(session: Session, lesson_id: uuid.UUID) -> LessonEdit:
    lesson = curriculum_repository.get_lesson_by_id(session, lesson_id)
    if lesson is None:
        raise AppError(404, "lesson_not_found", "Lesson not found.")
    return _lesson_edit(session, lesson)


def create_lesson(
    session: Session, actor: User, module_id: uuid.UUID, payload: LessonCreate, ip: str | None
) -> LessonEdit:
    module = curriculum_repository.get_module(session, module_id)
    if module is None:
        raise AppError(404, "module_not_found", "Module not found.")
    if not SLUG_PATTERN.fullmatch(payload.slug):
        raise AppError(422, "invalid_slug", "The slug may contain lowercase letters, digits and hyphens only.")
    if content_repository.lesson_slug_taken(session, module.id, payload.slug):
        raise AppError(409, "slug_taken", "This module already has a lesson with that slug.")
    concepts = _concepts(session, payload.concepts)
    content = _content(payload.content_md)

    lesson = Lesson(
        module_id=module.id,
        slug=payload.slug,
        title=payload.title,
        summary=payload.summary.strip(),
        position=content_repository.next_lesson_position(session, module.id),
        estimated_minutes=payload.minutes,
        status="published" if content else "planned",
        content_md=content,
        objectives=payload.objectives,
        principles=list(payload.principles),
        managed_in_app=True,
    )
    session.add(lesson)
    session.flush()
    content_repository.replace_lesson_concepts(session, lesson.id, [c.id for c in concepts.values()])
    _audit(session, actor, "content.lesson_created", ip, lesson_id=str(lesson.id), slug=lesson.slug)
    session.commit()
    return _lesson_edit(session, lesson)


def update_lesson(
    session: Session, actor: User, lesson_id: uuid.UUID, payload: LessonWrite, ip: str | None
) -> LessonEdit:
    lesson = curriculum_repository.get_lesson_by_id(session, lesson_id)
    if lesson is None:
        raise AppError(404, "lesson_not_found", "Lesson not found.")
    concepts = _concepts(session, payload.concepts)
    content = _content(payload.content_md)
    if lesson.status == "published" and content is None:
        raise AppError(
            422, "cannot_unpublish", "A published lesson must keep its content, because learners have progress on it."
        )

    lesson.title = payload.title
    lesson.summary = payload.summary.strip()
    lesson.estimated_minutes = payload.minutes
    lesson.objectives = payload.objectives
    lesson.principles = list(payload.principles)
    lesson.content_md = content
    lesson.status = "published" if content else "planned"
    lesson.managed_in_app = True
    content_repository.replace_lesson_concepts(session, lesson.id, [c.id for c in concepts.values()])
    _audit(session, actor, "content.lesson_updated", ip, lesson_id=str(lesson.id), slug=lesson.slug)
    session.commit()
    return _lesson_edit(session, lesson)


# ------------------------------------------------------------------ exercises
def _definition(kind: str, definition: dict[str, Any], concept_slugs: list[str]) -> dict[str, Any]:
    """Runs the same checks the curriculum files go through, so the app can never store something the grader cannot use."""
    item = dict(definition)
    try:
        if kind == "quiz":
            return _quiz(item, "definition", set(concept_slugs))
        if kind == "code":
            return _code(item, "definition", set(concept_slugs))
        return _puzzle(item, "definition")
    except CurriculumError as exc:
        raise AppError(422, "invalid_definition", str(exc)) from None
    except (TypeError, ValueError, KeyError, AttributeError):
        raise AppError(422, "invalid_definition", "The definition has the wrong shape for this exercise type.") from None


def _exercise_edit(session: Session, exercise: Exercise) -> ExerciseEdit:
    lesson = curriculum_repository.get_lesson_by_id(session, exercise.lesson_id)
    return ExerciseEdit(
        id=exercise.id,
        lesson_id=exercise.lesson_id,
        lesson_title=lesson.title if lesson else "",
        slug=exercise.slug,
        title=exercise.title,
        kind=exercise.kind,
        instructions_md=exercise.instructions_md,
        pass_score=exercise.pass_score,
        concepts=content_repository.exercise_concept_slugs(session, exercise.id),
        definition=exercise.definition,
        attempts=content_repository.count_exercise_submissions(session, exercise.id),
        managed_in_app=exercise.managed_in_app,
    )


def list_exercises(session: Session, lesson_id: uuid.UUID) -> list[ExerciseEdit]:
    if curriculum_repository.get_lesson_by_id(session, lesson_id) is None:
        raise AppError(404, "lesson_not_found", "Lesson not found.")
    return [_exercise_edit(session, e) for e in exercise_repository.list_for_lesson(session, lesson_id)]


def get_exercise(session: Session, exercise_id: uuid.UUID) -> ExerciseEdit:
    exercise = exercise_repository.get(session, exercise_id)
    if exercise is None:
        raise AppError(404, "exercise_not_found", "Exercise not found.")
    return _exercise_edit(session, exercise)


def create_exercise(
    session: Session, actor: User, lesson_id: uuid.UUID, payload: ExerciseCreate, ip: str | None
) -> ExerciseEdit:
    lesson = curriculum_repository.get_lesson_by_id(session, lesson_id)
    if lesson is None:
        raise AppError(404, "lesson_not_found", "Lesson not found.")
    if lesson.status != "published":
        raise AppError(409, "lesson_unavailable", "Write the lesson before adding exercises to it.")
    if not IDENT.fullmatch(payload.slug):
        raise AppError(422, "invalid_slug", "The slug may contain lowercase letters, digits, hyphens and underscores.")
    if content_repository.exercise_slug_taken(session, lesson.id, payload.slug):
        raise AppError(409, "slug_taken", "This lesson already has an exercise with that slug.")
    concepts = _concepts(session, payload.concepts)
    definition = _definition(payload.kind, payload.definition, payload.concepts)

    exercise = Exercise(
        lesson_id=lesson.id,
        slug=payload.slug,
        title=payload.title,
        kind=payload.kind,
        position=content_repository.next_exercise_position(session, lesson.id),
        instructions_md=payload.instructions_md,
        definition=definition,
        pass_score=payload.pass_score,
        managed_in_app=True,
    )
    session.add(exercise)
    session.flush()
    content_repository.replace_exercise_concepts(session, exercise.id, [c.id for c in concepts.values()])
    _audit(session, actor, "content.exercise_created", ip, exercise_id=str(exercise.id), slug=exercise.slug)
    session.commit()
    return _exercise_edit(session, exercise)


def update_exercise(
    session: Session, actor: User, exercise_id: uuid.UUID, payload: ExerciseWrite, ip: str | None
) -> ExerciseEdit:
    exercise = exercise_repository.get(session, exercise_id)
    if exercise is None:
        raise AppError(404, "exercise_not_found", "Exercise not found.")
    concepts = _concepts(session, payload.concepts)
    definition = _definition(exercise.kind, payload.definition, payload.concepts)

    exercise.title = payload.title
    exercise.instructions_md = payload.instructions_md
    exercise.pass_score = payload.pass_score
    exercise.definition = definition
    exercise.managed_in_app = True
    content_repository.replace_exercise_concepts(session, exercise.id, [c.id for c in concepts.values()])
    _audit(session, actor, "content.exercise_updated", ip, exercise_id=str(exercise.id), slug=exercise.slug)
    session.commit()
    return _exercise_edit(session, exercise)


def delete_exercise(session: Session, actor: User, exercise_id: uuid.UUID, ip: str | None) -> None:
    exercise = exercise_repository.get(session, exercise_id)
    if exercise is None:
        raise AppError(404, "exercise_not_found", "Exercise not found.")
    if content_repository.count_exercise_submissions(session, exercise.id) > 0:
        raise AppError(409, "has_submissions", "Learners have submitted this exercise, so it cannot be deleted.")
    _audit(session, actor, "content.exercise_deleted", ip, exercise_id=str(exercise.id), slug=exercise.slug)
    session.delete(exercise)
    session.commit()


# ------------------------------------------------------------------ projects
def _project_edit(project, course) -> ProjectEdit:
    return ProjectEdit(
        id=project.id,
        slug=project.slug,
        title=project.title,
        summary=project.summary,
        kind=project.kind,
        course_slug=course.slug,
        course_title=course.title,
        brief_md=project.brief_md,
        requirements=[Requirement(id=r["id"], text=r["text"]) for r in project.requirements],
        managed_in_app=project.managed_in_app,
    )


def get_project(session: Session, project_id: uuid.UUID) -> ProjectEdit:
    row = project_repository.get_project_with_course_by_id(session, project_id)
    if row is None:
        raise AppError(404, "project_not_found", "Project not found.")
    return _project_edit(*row)


def update_project(
    session: Session, actor: User, project_id: uuid.UUID, payload: ProjectWrite, ip: str | None
) -> ProjectEdit:
    row = project_repository.get_project_with_course_by_id(session, project_id)
    if row is None:
        raise AppError(404, "project_not_found", "Project not found.")
    project, course = row
    project.title = payload.title
    project.summary = payload.summary.strip()
    project.brief_md = payload.brief_md
    project.managed_in_app = True
    _audit(session, actor, "content.project_updated", ip, project_id=str(project.id), slug=project.slug)
    session.commit()
    return _project_edit(project, course)
