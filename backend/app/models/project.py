import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, false, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, CreatedAtMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Project(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A project is published exactly when its files exist in curriculum/projects/."""

    __tablename__ = "projects"
    __table_args__ = (
        UniqueConstraint("course_id", "slug", name="uq_projects_course_slug"),
        CheckConstraint("kind IN ('build', 'architecture', 'code_review')", name="kind_valid"),
        Index("ix_projects_course_id_position", "course_id", "position"),
    )

    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"))
    slug: Mapped[str] = mapped_column(String(80))
    title: Mapped[str] = mapped_column(String(200))
    summary: Mapped[str] = mapped_column(String(500), default="", server_default="")
    kind: Mapped[str] = mapped_column(String(16))
    position: Mapped[int] = mapped_column(Integer)
    brief_md: Mapped[str] = mapped_column(Text)
    requirements: Mapped[list[dict[str, str]]] = mapped_column(JSONB)
    managed_in_app: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false())


class ProjectConcept(Base):
    __tablename__ = "project_concepts"
    __table_args__ = (Index("ix_project_concepts_concept_id", "concept_id"),)

    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    concept_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("concepts.id", ondelete="RESTRICT"), primary_key=True)


class ProjectSubmission(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "project_submissions"
    __table_args__ = (
        UniqueConstraint("user_id", "project_id", name="uq_project_submissions_user_project"),
        CheckConstraint(
            "status IN ('draft', 'submitted', 'approved', 'changes_requested')", name="status_valid"
        ),
        CheckConstraint("status = 'draft' OR submitted_at IS NOT NULL", name="submitted_has_timestamp"),
        Index("ix_project_submissions_project_id", "project_id"),
        Index("ix_project_submissions_status_submitted_at", "status", "submitted_at"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="RESTRICT"))
    status: Mapped[str] = mapped_column(String(20), default="draft", server_default="draft")
    repo_url: Mapped[str | None] = mapped_column(String(200))
    documentation_md: Mapped[str] = mapped_column(Text, default="", server_default="")
    reflection_md: Mapped[str] = mapped_column(Text, default="", server_default="")
    requirement_checks: Mapped[dict[str, bool]] = mapped_column(
        JSONB, default=dict, server_default=text("'{}'::jsonb")
    )
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ProjectReview(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    """One row per review, so feedback history survives resubmission."""

    __tablename__ = "project_reviews"
    __table_args__ = (
        CheckConstraint("outcome IN ('approved', 'changes_requested')", name="outcome_valid"),
        Index("ix_project_reviews_submission_id_created_at", "submission_id", "created_at"),
        Index("ix_project_reviews_reviewer_id", "reviewer_id"),
    )

    submission_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("project_submissions.id", ondelete="CASCADE"))
    reviewer_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    outcome: Mapped[str] = mapped_column(String(20))
    rubric_scores: Mapped[dict[str, Any]] = mapped_column(JSONB)
    feedback: Mapped[str] = mapped_column(Text)


class UserAchievement(Base):
    """Only earned achievements are stored. The catalog lives in code (services/achievement_service.py)."""

    __tablename__ = "user_achievements"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    achievement_key: Mapped[str] = mapped_column(String(40), primary_key=True)
    earned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
