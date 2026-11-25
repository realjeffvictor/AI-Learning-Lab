"""curriculum engine: concepts, courses, modules, lessons, enrollments, progress, competencies

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-25
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "concepts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("category", sa.String(length=1), nullable=False),
        sa.Column("description", sa.String(length=500), server_default="", nullable=False),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_concepts")),
        sa.UniqueConstraint("slug", name=op.f("uq_concepts_slug")),
        sa.CheckConstraint("category IN ('A', 'B', 'C')", name=op.f("ck_concepts_category_valid")),
    )

    op.create_table(
        "courses",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("summary", sa.String(length=1000), server_default="", nullable=False),
        sa.Column("kind", sa.String(length=10), nullable=False),
        sa.Column("stage_number", sa.Integer(), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_courses")),
        sa.UniqueConstraint("slug", name=op.f("uq_courses_slug")),
        sa.UniqueConstraint("stage_number", name=op.f("uq_courses_stage_number")),
        sa.CheckConstraint("kind IN ('stage', 'track')", name=op.f("ck_courses_kind_valid")),
        sa.CheckConstraint(
            "(kind = 'stage') = (stage_number IS NOT NULL)", name=op.f("ck_courses_stage_number_matches_kind")
        ),
    )
    op.create_index(op.f("ix_courses_position"), "courses", ["position"])

    op.create_table(
        "modules",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("course_id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("summary", sa.String(length=1000), server_default="", nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["course_id"], ["courses.id"], name=op.f("fk_modules_course_id_courses"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_modules")),
        sa.UniqueConstraint("course_id", "slug", name=op.f("uq_modules_course_slug")),
    )
    op.create_index(op.f("ix_modules_course_id_position"), "modules", ["course_id", "position"])

    op.create_table(
        "lessons",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("module_id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("summary", sa.String(length=500), server_default="", nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("estimated_minutes", sa.Integer(), server_default="10", nullable=False),
        sa.Column("status", sa.String(length=10), server_default="planned", nullable=False),
        sa.Column("content_md", sa.Text(), nullable=True),
        sa.Column("objectives", postgresql.JSONB(), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("principles", postgresql.JSONB(), server_default=sa.text("'[]'::jsonb"), nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["module_id"], ["modules.id"], name=op.f("fk_lessons_module_id_modules"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_lessons")),
        sa.UniqueConstraint("module_id", "slug", name=op.f("uq_lessons_module_slug")),
        sa.CheckConstraint("status IN ('published', 'planned')", name=op.f("ck_lessons_status_valid")),
        sa.CheckConstraint("estimated_minutes > 0", name=op.f("ck_lessons_estimated_minutes_positive")),
        sa.CheckConstraint(
            "(status = 'published') = (content_md IS NOT NULL)", name=op.f("ck_lessons_published_has_content")
        ),
    )
    op.create_index(op.f("ix_lessons_module_id_position"), "lessons", ["module_id", "position"])

    op.create_table(
        "lesson_concepts",
        sa.Column("lesson_id", sa.Uuid(), nullable=False),
        sa.Column("concept_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["lesson_id"], ["lessons.id"], name=op.f("fk_lesson_concepts_lesson_id_lessons"), ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["concept_id"], ["concepts.id"], name=op.f("fk_lesson_concepts_concept_id_concepts"), ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("lesson_id", "concept_id", name=op.f("pk_lesson_concepts")),
    )
    op.create_index(op.f("ix_lesson_concepts_concept_id"), "lesson_concepts", ["concept_id"])

    op.create_table(
        "enrollments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("course_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_enrollments_user_id_users"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["course_id"], ["courses.id"], name=op.f("fk_enrollments_course_id_courses"), ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_enrollments")),
        sa.UniqueConstraint("user_id", "course_id", name=op.f("uq_enrollments_user_course")),
    )
    op.create_index(op.f("ix_enrollments_course_id"), "enrollments", ["course_id"])

    op.create_table(
        "lesson_progress",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("lesson_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=12), server_default="in_progress", nullable=False),
        sa.Column("time_spent_seconds", sa.Integer(), server_default="0", nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_visited_at", sa.DateTime(timezone=True), nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_lesson_progress_user_id_users"), ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["lesson_id"], ["lessons.id"], name=op.f("fk_lesson_progress_lesson_id_lessons"), ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_lesson_progress")),
        sa.UniqueConstraint("user_id", "lesson_id", name=op.f("uq_lesson_progress_user_lesson")),
        sa.CheckConstraint("status IN ('in_progress', 'completed')", name=op.f("ck_lesson_progress_status_valid")),
        sa.CheckConstraint("time_spent_seconds >= 0", name=op.f("ck_lesson_progress_time_non_negative")),
        sa.CheckConstraint(
            "(status = 'completed') = (completed_at IS NOT NULL)",
            name=op.f("ck_lesson_progress_completed_matches_status"),
        ),
    )
    op.create_index(op.f("ix_lesson_progress_lesson_id"), "lesson_progress", ["lesson_id"])

    op.create_table(
        "user_competencies",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("concept_id", sa.Uuid(), nullable=False),
        sa.Column("lessons_completed", sa.Integer(), server_default="0", nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_user_competencies_user_id_users"), ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["concept_id"], ["concepts.id"], name=op.f("fk_user_competencies_concept_id_concepts"), ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("user_id", "concept_id", name=op.f("pk_user_competencies")),
        sa.CheckConstraint("lessons_completed >= 0", name=op.f("ck_user_competencies_lessons_completed_non_negative")),
    )
    op.create_index(op.f("ix_user_competencies_concept_id"), "user_competencies", ["concept_id"])


def downgrade() -> None:
    op.drop_table("user_competencies")
    op.drop_table("lesson_progress")
    op.drop_table("enrollments")
    op.drop_table("lesson_concepts")
    op.drop_table("lessons")
    op.drop_table("modules")
    op.drop_table("courses")
    op.drop_table("concepts")
