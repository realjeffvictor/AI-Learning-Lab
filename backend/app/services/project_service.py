import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.project_rules import MIN_DOCUMENTATION_CHARS, MIN_REFLECTION_CHARS
from app.core.security import utcnow
from app.models import Project, ProjectSubmission
from app.repositories import audit_repository, project_repository
from app.schemas.curriculum import ConceptRead
from app.schemas.project import ProjectDetail, ProjectSummary, Requirement, ReviewRead, SubmissionRead
from app.services import achievement_service

LOCKED_STATUSES = ("submitted", "approved")


def submission_read(submission: ProjectSubmission) -> SubmissionRead:
    return SubmissionRead.model_validate(submission)


def requirements_of(project: Project) -> list[Requirement]:
    return [Requirement(id=item["id"], text=item["text"]) for item in project.requirements]


def review_reads(session: Session, submission_id: uuid.UUID) -> list[ReviewRead]:
    return [
        ReviewRead(
            id=review.id,
            outcome=review.outcome,
            rubric_scores={key: int(value) for key, value in review.rubric_scores.items()},
            feedback=review.feedback,
            created_at=review.created_at,
            reviewer_name=name,
        )
        for review, name in project_repository.list_reviews(session, submission_id)
    ]


def list_projects(session: Session, user_id: uuid.UUID) -> list[ProjectSummary]:
    submissions = project_repository.submissions_for_user(session, user_id)
    return [
        ProjectSummary(
            id=project.id,
            slug=project.slug,
            title=project.title,
            summary=project.summary,
            kind=project.kind,
            course_slug=course.slug,
            course_title=course.title,
            status=submissions[project.id].status if project.id in submissions else "not_started",
            requirements_count=len(project.requirements),
        )
        for project, course in project_repository.list_projects(session)
    ]


def get_project(session: Session, user_id: uuid.UUID, course_slug: str, project_slug: str) -> ProjectDetail:
    row = project_repository.get_project_with_course(session, course_slug, project_slug)
    if row is None:
        raise AppError(404, "project_not_found", "Project not found.")
    project, course = row
    submission = project_repository.get_submission(session, user_id, project.id)
    concepts = [
        ConceptRead(slug=c.slug, name=c.name, category=c.category)
        for c in project_repository.concepts_for(session, project.id)
    ]
    return ProjectDetail(
        id=project.id,
        slug=project.slug,
        title=project.title,
        summary=project.summary,
        kind=project.kind,
        course_slug=course.slug,
        course_title=course.title,
        brief_md=project.brief_md,
        requirements=requirements_of(project),
        requires_repo=project.kind == "build",
        concepts=concepts,
        min_documentation_chars=MIN_DOCUMENTATION_CHARS[project.kind],
        min_reflection_chars=MIN_REFLECTION_CHARS,
        submission=submission_read(submission) if submission else None,
        reviews=review_reads(session, submission.id) if submission else [],
    )


def save_draft(
    session: Session, user_id: uuid.UUID, project_id: uuid.UUID, changes: dict[str, Any]
) -> SubmissionRead:
    project = project_repository.get_project(session, project_id)
    if project is None:
        raise AppError(404, "project_not_found", "Project not found.")
    if changes.get("repo_url") is not None and project.kind != "build":
        raise AppError(422, "repo_not_applicable", "This project does not use a repository link.")
    checks = changes.get("requirement_checks")
    if checks is not None and not set(checks) <= {item["id"] for item in project.requirements}:
        raise AppError(422, "invalid_requirement", "One of the ticked requirements does not belong to this project.")

    project_repository.ensure_submission(session, user_id, project.id)
    submission = project_repository.get_submission(session, user_id, project.id, for_update=True)
    assert submission is not None
    if submission.status in LOCKED_STATUSES:
        raise AppError(
            409, "submission_locked", "This submission is locked while it is awaiting review or after approval."
        )

    if "repo_url" in changes:
        submission.repo_url = changes["repo_url"]
    if "documentation_md" in changes:
        submission.documentation_md = changes["documentation_md"] or ""
    if "reflection_md" in changes:
        submission.reflection_md = changes["reflection_md"] or ""
    if "requirement_checks" in changes:
        submission.requirement_checks = changes["requirement_checks"] or {}
    session.commit()
    return submission_read(submission)


def completeness_problems(project: Project, submission: ProjectSubmission) -> list[str]:
    problems: list[str] = []
    if project.kind == "build" and not submission.repo_url:
        problems.append("Add your GitHub repository link.")
    unmet = [item for item in project.requirements if not submission.requirement_checks.get(item["id"])]
    if unmet:
        problems.append(f"Tick every requirement you have met ({len(unmet)} left).")
    minimum_doc = MIN_DOCUMENTATION_CHARS[project.kind]
    doc_length = len(submission.documentation_md.strip())
    if doc_length < minimum_doc:
        problems.append(f"Documentation needs at least {minimum_doc} characters (you have {doc_length}).")
    reflection_length = len(submission.reflection_md.strip())
    if reflection_length < MIN_REFLECTION_CHARS:
        problems.append(f"Reflection needs at least {MIN_REFLECTION_CHARS} characters (you have {reflection_length}).")
    return problems


def submit(session: Session, user_id: uuid.UUID, project_id: uuid.UUID, ip: str | None) -> SubmissionRead:
    project = project_repository.get_project(session, project_id)
    if project is None:
        raise AppError(404, "project_not_found", "Project not found.")
    submission = project_repository.get_submission(session, user_id, project.id, for_update=True)
    if submission is None:
        raise AppError(409, "no_draft", "Save a draft before submitting.")
    if submission.status in LOCKED_STATUSES:
        raise AppError(409, "submission_locked", "This submission has already been submitted.")

    problems = completeness_problems(project, submission)
    if problems:
        raise AppError(422, "submission_incomplete", " ".join(problems))

    submission.status = "submitted"
    submission.submitted_at = utcnow()
    audit_repository.record(
        session, "project.submitted", actor_user_id=user_id, ip_address=ip, details={"project_id": str(project.id)}
    )
    achievement_service.sync(session, user_id)
    session.commit()
    return submission_read(submission)
