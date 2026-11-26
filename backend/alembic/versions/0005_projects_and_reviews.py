"""projects, submissions, reviews and achievements

Revision ID: 0005
Revises: 0004
Create Date: 2026-11-26
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("course_id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("summary", sa.String(length=500), server_default="", nullable=False),
        sa.Column("kind", sa.String(length=16), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("brief_md", sa.Text(), nullable=False),
        sa.Column("requirements", postgresql.JSONB(), nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["course_id"], ["courses.id"], name=op.f("fk_projects_course_id_courses"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_projects")),
        sa.UniqueConstraint("course_id", "slug", name=op.f("uq_projects_course_slug")),
        sa.CheckConstraint(
            "kind IN ('build', 'architecture', 'code_review')", name=op.f("ck_projects_kind_valid")
        ),
    )
    op.create_index(op.f("ix_projects_course_id_position"), "projects", ["course_id", "position"])

    op.create_table(
        "project_concepts",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("concept_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["project_id"], ["projects.id"], name=op.f("fk_project_concepts_project_id_projects"), ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["concept_id"], ["concepts.id"], name=op.f("fk_project_concepts_concept_id_concepts"), ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("project_id", "concept_id", name=op.f("pk_project_concepts")),
    )
    op.create_index(op.f("ix_project_concepts_concept_id"), "project_concepts", ["concept_id"])

    op.create_table(
        "project_submissions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="draft", nullable=False),
        sa.Column("repo_url", sa.String(length=200), nullable=True),
        sa.Column("documentation_md", sa.Text(), server_default="", nullable=False),
        sa.Column("reflection_md", sa.Text(), server_default="", nullable=False),
        sa.Column("requirement_checks", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_project_submissions_user_id_users"), ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_project_submissions_project_id_projects"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_project_submissions")),
        sa.UniqueConstraint("user_id", "project_id", name=op.f("uq_project_submissions_user_project")),
        sa.CheckConstraint(
            "status IN ('draft', 'submitted', 'approved', 'changes_requested')",
            name=op.f("ck_project_submissions_status_valid"),
        ),
        sa.CheckConstraint(
            "status = 'draft' OR submitted_at IS NOT NULL", name=op.f("ck_project_submissions_submitted_has_timestamp")
        ),
    )
    op.create_index(op.f("ix_project_submissions_project_id"), "project_submissions", ["project_id"])
    op.create_index(
        op.f("ix_project_submissions_status_submitted_at"), "project_submissions", ["status", "submitted_at"]
    )

    op.create_table(
        "project_reviews",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("submission_id", sa.Uuid(), nullable=False),
        sa.Column("reviewer_id", sa.Uuid(), nullable=True),
        sa.Column("outcome", sa.String(length=20), nullable=False),
        sa.Column("rubric_scores", postgresql.JSONB(), nullable=False),
        sa.Column("feedback", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["submission_id"],
            ["project_submissions.id"],
            name=op.f("fk_project_reviews_submission_id_project_submissions"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["reviewer_id"], ["users.id"], name=op.f("fk_project_reviews_reviewer_id_users"), ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_project_reviews")),
        sa.CheckConstraint(
            "outcome IN ('approved', 'changes_requested')", name=op.f("ck_project_reviews_outcome_valid")
        ),
    )
    op.create_index(
        op.f("ix_project_reviews_submission_id_created_at"), "project_reviews", ["submission_id", "created_at"]
    )
    op.create_index(op.f("ix_project_reviews_reviewer_id"), "project_reviews", ["reviewer_id"])

    op.create_table(
        "user_achievements",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("achievement_key", sa.String(length=40), nullable=False),
        sa.Column("earned_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_user_achievements_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("user_id", "achievement_key", name=op.f("pk_user_achievements")),
    )


def downgrade() -> None:
    op.drop_table("user_achievements")
    op.drop_table("project_reviews")
    op.drop_table("project_submissions")
    op.drop_table("project_concepts")
    op.drop_table("projects")
