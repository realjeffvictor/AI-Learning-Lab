import uuid

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.models import Concept, Course, Project, ProjectConcept, ProjectReview, ProjectSubmission, User, UserProfile


def list_projects(session: Session):
    return session.execute(
        select(Project, Course)
        .join(Course, Course.id == Project.course_id)
        .order_by(Course.position, Project.position, Project.slug)
    ).all()


def get_project(session: Session, project_id: uuid.UUID) -> Project | None:
    return session.get(Project, project_id)


def get_project_with_course(session: Session, course_slug: str, project_slug: str):
    return session.execute(
        select(Project, Course)
        .join(Course, Course.id == Project.course_id)
        .where(Course.slug == course_slug, Project.slug == project_slug)
    ).first()


def get_project_with_course_by_id(session: Session, project_id: uuid.UUID):
    return session.execute(
        select(Project, Course).join(Course, Course.id == Project.course_id).where(Project.id == project_id)
    ).first()


def concepts_for(session: Session, project_id: uuid.UUID) -> list[Concept]:
    return list(
        session.scalars(
            select(Concept)
            .join(ProjectConcept, ProjectConcept.concept_id == Concept.id)
            .where(ProjectConcept.project_id == project_id)
            .order_by(Concept.category, Concept.name)
        )
    )


def submissions_for_user(session: Session, user_id: uuid.UUID) -> dict[uuid.UUID, ProjectSubmission]:
    rows = session.scalars(select(ProjectSubmission).where(ProjectSubmission.user_id == user_id))
    return {row.project_id: row for row in rows}


def get_submission(
    session: Session, user_id: uuid.UUID, project_id: uuid.UUID, for_update: bool = False
) -> ProjectSubmission | None:
    statement = select(ProjectSubmission).where(
        ProjectSubmission.user_id == user_id, ProjectSubmission.project_id == project_id
    )
    if for_update:
        statement = statement.with_for_update().execution_options(populate_existing=True)
    return session.scalar(statement)


def get_submission_by_id(
    session: Session, submission_id: uuid.UUID, for_update: bool = False
) -> ProjectSubmission | None:
    statement = select(ProjectSubmission).where(ProjectSubmission.id == submission_id)
    if for_update:
        statement = statement.with_for_update().execution_options(populate_existing=True)
    return session.scalar(statement)


def ensure_submission(session: Session, user_id: uuid.UUID, project_id: uuid.UUID) -> None:
    session.execute(
        pg_insert(ProjectSubmission)
        .values(
            id=uuid.uuid4(),
            user_id=user_id,
            project_id=project_id,
            status="draft",
            documentation_md="",
            reflection_md="",
            requirement_checks={},
        )
        .on_conflict_do_nothing(index_elements=["user_id", "project_id"])
    )


def list_reviews(session: Session, submission_id: uuid.UUID) -> list[tuple[ProjectReview, str | None]]:
    rows = session.execute(
        select(ProjectReview, UserProfile.display_name)
        .outerjoin(UserProfile, UserProfile.user_id == ProjectReview.reviewer_id)
        .where(ProjectReview.submission_id == submission_id)
        .order_by(ProjectReview.created_at.desc(), ProjectReview.id.desc())
    ).all()
    return [(review, name) for review, name in rows]


def add_review(session: Session, review: ProjectReview) -> ProjectReview:
    session.add(review)
    session.flush()
    return review


def learner_info(session: Session, user_id: uuid.UUID) -> tuple[str, str]:
    row = session.execute(
        select(UserProfile.display_name, User.email)
        .select_from(User)
        .join(UserProfile, UserProfile.user_id == User.id)
        .where(User.id == user_id)
    ).first()
    return (row.display_name, row.email) if row else ("Unknown", "")


def queue_page(session: Session, page: int, page_size: int):
    total = session.scalar(
        select(func.count()).select_from(ProjectSubmission).where(ProjectSubmission.status == "submitted")
    )
    rows = session.execute(
        select(
            ProjectSubmission.id.label("submission_id"),
            ProjectSubmission.submitted_at,
            Project.title.label("project_title"),
            Project.kind.label("project_kind"),
            Course.slug.label("course_slug"),
            Course.title.label("course_title"),
            UserProfile.display_name,
            User.email,
        )
        .select_from(ProjectSubmission)
        .join(Project, Project.id == ProjectSubmission.project_id)
        .join(Course, Course.id == Project.course_id)
        .join(User, User.id == ProjectSubmission.user_id)
        .join(UserProfile, UserProfile.user_id == User.id)
        .where(ProjectSubmission.status == "submitted")
        .order_by(ProjectSubmission.submitted_at, ProjectSubmission.id)
        .limit(page_size)
        .offset((page - 1) * page_size)
    ).all()
    return rows, int(total or 0)
