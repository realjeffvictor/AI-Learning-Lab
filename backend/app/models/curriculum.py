import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, CreatedAtMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Concept(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A unit of the taxonomy used for competency tracking. Category A/B/C matches the three competence categories."""

    __tablename__ = "concepts"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_concepts_slug"),
        CheckConstraint("category IN ('A', 'B', 'C')", name="category_valid"),
    )

    slug: Mapped[str] = mapped_column(String(80))
    name: Mapped[str] = mapped_column(String(120))
    category: Mapped[str] = mapped_column(String(1))
    description: Mapped[str] = mapped_column(String(500), default="", server_default="")


class Course(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "courses"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_courses_slug"),
        UniqueConstraint("stage_number", name="uq_courses_stage_number"),
        CheckConstraint("kind IN ('stage', 'track')", name="kind_valid"),
        CheckConstraint("(kind = 'stage') = (stage_number IS NOT NULL)", name="stage_number_matches_kind"),
        Index("ix_courses_position", "position"),
    )

    slug: Mapped[str] = mapped_column(String(80))
    title: Mapped[str] = mapped_column(String(200))
    summary: Mapped[str] = mapped_column(String(1000), default="", server_default="")
    kind: Mapped[str] = mapped_column(String(10))
    stage_number: Mapped[int | None] = mapped_column(Integer)
    position: Mapped[int] = mapped_column(Integer)

    modules: Mapped[list["Module"]] = relationship(
        back_populates="course", order_by="Module.position", passive_deletes=True
    )


class Module(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "modules"
    __table_args__ = (
        UniqueConstraint("course_id", "slug", name="uq_modules_course_slug"),
        Index("ix_modules_course_id_position", "course_id", "position"),
    )

    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"))
    slug: Mapped[str] = mapped_column(String(80))
    title: Mapped[str] = mapped_column(String(200))
    summary: Mapped[str] = mapped_column(String(1000), default="", server_default="")
    position: Mapped[int] = mapped_column(Integer)

    course: Mapped[Course] = relationship(back_populates="modules")
    lessons: Mapped[list["Lesson"]] = relationship(
        back_populates="module", order_by="Lesson.position", passive_deletes=True
    )


class Lesson(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A lesson is 'published' exactly when it has Markdown content. Everything else is 'planned'."""

    __tablename__ = "lessons"
    __table_args__ = (
        UniqueConstraint("module_id", "slug", name="uq_lessons_module_slug"),
        CheckConstraint("status IN ('published', 'planned')", name="status_valid"),
        CheckConstraint("estimated_minutes > 0", name="estimated_minutes_positive"),
        CheckConstraint("(status = 'published') = (content_md IS NOT NULL)", name="published_has_content"),
        Index("ix_lessons_module_id_position", "module_id", "position"),
    )

    module_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("modules.id", ondelete="CASCADE"))
    slug: Mapped[str] = mapped_column(String(100))
    title: Mapped[str] = mapped_column(String(200))
    summary: Mapped[str] = mapped_column(String(500), default="", server_default="")
    position: Mapped[int] = mapped_column(Integer)
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=10, server_default="10")
    status: Mapped[str] = mapped_column(String(10), default="planned", server_default="planned")
    content_md: Mapped[str | None] = mapped_column(Text)
    objectives: Mapped[list[str]] = mapped_column(JSONB, default=list, server_default=text("'[]'::jsonb"))
    principles: Mapped[list[str]] = mapped_column(JSONB, default=list, server_default=text("'[]'::jsonb"))

    module: Mapped[Module] = relationship(back_populates="lessons")


class LessonConcept(Base):
    __tablename__ = "lesson_concepts"
    __table_args__ = (Index("ix_lesson_concepts_concept_id", "concept_id"),)

    lesson_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"), primary_key=True)
    concept_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("concepts.id", ondelete="RESTRICT"), primary_key=True)


class Enrollment(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="uq_enrollments_user_course"),
        Index("ix_enrollments_course_id", "course_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="RESTRICT"))


class LessonProgress(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "lesson_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "lesson_id", name="uq_lesson_progress_user_lesson"),
        CheckConstraint("status IN ('in_progress', 'completed')", name="status_valid"),
        CheckConstraint("time_spent_seconds >= 0", name="time_non_negative"),
        CheckConstraint("(status = 'completed') = (completed_at IS NOT NULL)", name="completed_matches_status"),
        Index("ix_lesson_progress_lesson_id", "lesson_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    lesson_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lessons.id", ondelete="RESTRICT"))
    status: Mapped[str] = mapped_column(String(12), default="in_progress", server_default="in_progress")
    time_spent_seconds: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_visited_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class UserCompetency(TimestampMixin, Base):
    """Exposure only: how many completed lessons touched a concept. Skill levels come from graded exercises later."""

    __tablename__ = "user_competencies"
    __table_args__ = (
        CheckConstraint("lessons_completed >= 0", name="lessons_completed_non_negative"),
        Index("ix_user_competencies_concept_id", "concept_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    concept_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("concepts.id", ondelete="RESTRICT"), primary_key=True)
    lessons_completed: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
