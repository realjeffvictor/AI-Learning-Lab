import uuid
from typing import Any

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Index, Integer, String, Text, UniqueConstraint, false
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, CreatedAtMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Exercise(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """definition holds everything kind-specific, including answers. It is never sent to clients as stored."""

    __tablename__ = "exercises"
    __table_args__ = (
        UniqueConstraint("lesson_id", "slug", name="uq_exercises_lesson_slug"),
        CheckConstraint("kind IN ('code', 'quiz', 'puzzle')", name="kind_valid"),
        CheckConstraint("pass_score BETWEEN 1 AND 100", name="pass_score_valid"),
        Index("ix_exercises_lesson_id_position", "lesson_id", "position"),
    )

    lesson_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"))
    slug: Mapped[str] = mapped_column(String(80))
    title: Mapped[str] = mapped_column(String(200))
    kind: Mapped[str] = mapped_column(String(10))
    position: Mapped[int] = mapped_column(Integer)
    instructions_md: Mapped[str] = mapped_column(Text)
    definition: Mapped[dict[str, Any]] = mapped_column(JSONB)
    pass_score: Mapped[int] = mapped_column(Integer, default=70, server_default="70")
    managed_in_app: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false())


class ExerciseConcept(Base):
    __tablename__ = "exercise_concepts"
    __table_args__ = (Index("ix_exercise_concepts_concept_id", "concept_id"),)

    exercise_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exercises.id", ondelete="CASCADE"), primary_key=True)
    concept_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("concepts.id", ondelete="RESTRICT"), primary_key=True)


class Submission(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "submissions"
    __table_args__ = (
        CheckConstraint("score BETWEEN 0 AND 100", name="score_valid"),
        Index("ix_submissions_user_id_exercise_id_created_at", "user_id", "exercise_id", "created_at"),
        Index("ix_submissions_exercise_id", "exercise_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    exercise_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exercises.id", ondelete="RESTRICT"))
    answer: Mapped[dict[str, Any]] = mapped_column(JSONB)
    score: Mapped[int] = mapped_column(Integer)
    passed: Mapped[bool] = mapped_column(Boolean)


class SubmissionConceptResult(Base):
    __tablename__ = "submission_concept_results"
    __table_args__ = (
        CheckConstraint("total > 0", name="total_positive"),
        CheckConstraint("correct >= 0 AND correct <= total", name="correct_in_range"),
        Index("ix_submission_concept_results_concept_id", "concept_id"),
    )

    submission_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("submissions.id", ondelete="CASCADE"), primary_key=True)
    concept_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("concepts.id", ondelete="RESTRICT"), primary_key=True)
    correct: Mapped[int] = mapped_column(Integer)
    total: Mapped[int] = mapped_column(Integer)


class Resource(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Curated external learning material. The platform only ever recommends rows that exist here."""

    __tablename__ = "resources"
    __table_args__ = (
        UniqueConstraint("url", name="uq_resources_url"),
        CheckConstraint("kind IN ('youtube', 'article', 'docs', 'course', 'repo')", name="kind_valid"),
        CheckConstraint("level IN ('beginner', 'intermediate', 'advanced')", name="level_valid"),
        Index("ix_resources_concept_id", "concept_id"),
    )

    title: Mapped[str] = mapped_column(String(200))
    url: Mapped[str] = mapped_column(String(500))
    kind: Mapped[str] = mapped_column(String(10))
    concept_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("concepts.id", ondelete="RESTRICT"))
    level: Mapped[str] = mapped_column(String(12))
    is_open_source: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false())
