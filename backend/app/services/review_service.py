import uuid

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.project_rules import MIN_APPROVAL_SCORE
from app.models import ProjectReview, User
from app.repositories import audit_repository, project_repository
from app.schemas.project import QueueItem, QueuePage, ReviewDetail, ReviewRequest
from app.services import achievement_service, notification_service, project_service


def queue(session: Session, page: int, page_size: int) -> QueuePage:
    rows, total = project_repository.queue_page(session, page, page_size)
    items = [
        QueueItem(
            submission_id=row.submission_id,
            project_title=row.project_title,
            project_kind=row.project_kind,
            course_slug=row.course_slug,
            course_title=row.course_title,
            learner_name=row.display_name,
            learner_email=row.email,
            submitted_at=row.submitted_at,
        )
        for row in rows
    ]
    return QueuePage(items=items, page=page, page_size=page_size, total=total)


def get_detail(session: Session, submission_id: uuid.UUID) -> ReviewDetail:
    submission = project_repository.get_submission_by_id(session, submission_id)
    # Drafts are the learner's private work in progress, so reviewers cannot see them.
    if submission is None or submission.status == "draft":
        raise AppError(404, "submission_not_found", "Submission not found.")
    row = project_repository.get_project_with_course_by_id(session, submission.project_id)
    assert row is not None
    project, course = row
    name, email = project_repository.learner_info(session, submission.user_id)
    return ReviewDetail(
        submission=project_service.submission_read(submission),
        project_title=project.title,
        project_kind=project.kind,
        course_slug=course.slug,
        course_title=course.title,
        brief_md=project.brief_md,
        requirements=project_service.requirements_of(project),
        learner_name=name,
        learner_email=email,
        reviews=project_service.review_reads(session, submission.id),
    )


def review(
    session: Session, reviewer: User, submission_id: uuid.UUID, request: ReviewRequest, ip: str | None
) -> ReviewDetail:
    submission = project_repository.get_submission_by_id(session, submission_id, for_update=True)
    if submission is None:
        raise AppError(404, "submission_not_found", "Submission not found.")
    if submission.user_id == reviewer.id:
        raise AppError(403, "cannot_review_own", "You cannot review your own submission.")
    if submission.status != "submitted":
        raise AppError(409, "not_awaiting_review", "This submission is not awaiting review.")

    scores = request.rubric_scores.model_dump()
    if request.outcome == "approved" and min(scores.values()) < MIN_APPROVAL_SCORE:
        raise AppError(
            422, "rubric_too_low", f"Approval needs a score of at least {MIN_APPROVAL_SCORE} on every criterion."
        )

    project_repository.add_review(
        session,
        ProjectReview(
            submission_id=submission.id,
            reviewer_id=reviewer.id,
            outcome=request.outcome,
            rubric_scores=scores,
            feedback=request.feedback,
        ),
    )
    submission.status = request.outcome
    audit_repository.record(
        session,
        "project.reviewed",
        actor_user_id=reviewer.id,
        ip_address=ip,
        details={"submission_id": str(submission.id), "outcome": request.outcome},
    )
    notification_service.notify_review(session, submission, request.outcome)
    achievement_service.sync(session, submission.user_id)
    session.commit()
    return get_detail(session, submission.id)
