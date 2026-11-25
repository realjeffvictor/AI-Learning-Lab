"""exercises, submissions, per-concept results and curated resources

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-25
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "exercises",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("lesson_id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("kind", sa.String(length=10), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("instructions_md", sa.Text(), nullable=False),
        sa.Column("definition", postgresql.JSONB(), nullable=False),
        sa.Column("pass_score", sa.Integer(), server_default="70", nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["lesson_id"], ["lessons.id"], name=op.f("fk_exercises_lesson_id_lessons"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_exercises")),
        sa.UniqueConstraint("lesson_id", "slug", name=op.f("uq_exercises_lesson_slug")),
        sa.CheckConstraint("kind IN ('code', 'quiz', 'puzzle')", name=op.f("ck_exercises_kind_valid")),
        sa.CheckConstraint("pass_score BETWEEN 1 AND 100", name=op.f("ck_exercises_pass_score_valid")),
    )
    op.create_index(op.f("ix_exercises_lesson_id_position"), "exercises", ["lesson_id", "position"])

    op.create_table(
        "exercise_concepts",
        sa.Column("exercise_id", sa.Uuid(), nullable=False),
        sa.Column("concept_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["exercise_id"], ["exercises.id"], name=op.f("fk_exercise_concepts_exercise_id_exercises"), ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["concept_id"], ["concepts.id"], name=op.f("fk_exercise_concepts_concept_id_concepts"), ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("exercise_id", "concept_id", name=op.f("pk_exercise_concepts")),
    )
    op.create_index(op.f("ix_exercise_concepts_concept_id"), "exercise_concepts", ["concept_id"])

    op.create_table(
        "submissions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("exercise_id", sa.Uuid(), nullable=False),
        sa.Column("answer", postgresql.JSONB(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_submissions_user_id_users"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["exercise_id"], ["exercises.id"], name=op.f("fk_submissions_exercise_id_exercises"), ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_submissions")),
        sa.CheckConstraint("score BETWEEN 0 AND 100", name=op.f("ck_submissions_score_valid")),
    )
    op.create_index(
        op.f("ix_submissions_user_id_exercise_id_created_at"), "submissions", ["user_id", "exercise_id", "created_at"]
    )
    op.create_index(op.f("ix_submissions_exercise_id"), "submissions", ["exercise_id"])

    op.create_table(
        "submission_concept_results",
        sa.Column("submission_id", sa.Uuid(), nullable=False),
        sa.Column("concept_id", sa.Uuid(), nullable=False),
        sa.Column("correct", sa.Integer(), nullable=False),
        sa.Column("total", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["submission_id"],
            ["submissions.id"],
            name=op.f("fk_submission_concept_results_submission_id_submissions"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["concept_id"],
            ["concepts.id"],
            name=op.f("fk_submission_concept_results_concept_id_concepts"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("submission_id", "concept_id", name=op.f("pk_submission_concept_results")),
        sa.CheckConstraint("total > 0", name=op.f("ck_submission_concept_results_total_positive")),
        sa.CheckConstraint(
            "correct >= 0 AND correct <= total", name=op.f("ck_submission_concept_results_correct_in_range")
        ),
    )
    op.create_index(
        op.f("ix_submission_concept_results_concept_id"), "submission_concept_results", ["concept_id"]
    )

    op.create_table(
        "resources",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("url", sa.String(length=500), nullable=False),
        sa.Column("kind", sa.String(length=10), nullable=False),
        sa.Column("concept_id", sa.Uuid(), nullable=False),
        sa.Column("level", sa.String(length=12), nullable=False),
        sa.Column("is_open_source", sa.Boolean(), server_default=sa.false(), nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["concept_id"], ["concepts.id"], name=op.f("fk_resources_concept_id_concepts"), ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_resources")),
        sa.UniqueConstraint("url", name=op.f("uq_resources_url")),
        sa.CheckConstraint(
            "kind IN ('youtube', 'article', 'docs', 'course', 'repo')", name=op.f("ck_resources_kind_valid")
        ),
        sa.CheckConstraint("level IN ('beginner', 'intermediate', 'advanced')", name=op.f("ck_resources_level_valid")),
    )
    op.create_index(op.f("ix_resources_concept_id"), "resources", ["concept_id"])


def downgrade() -> None:
    op.drop_table("resources")
    op.drop_table("submission_concept_results")
    op.drop_table("submissions")
    op.drop_table("exercise_concepts")
    op.drop_table("exercises")
