"""rate limit hits and certificates

Revision ID: 0007
Revises: 0006
Create Date: 2026-11-26
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "rate_limit_hits",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("bucket", sa.String(length=40), nullable=False),
        sa.Column("key", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_rate_limit_hits")),
    )
    op.create_index(
        op.f("ix_rate_limit_hits_bucket_key_created_at"), "rate_limit_hits", ["bucket", "key", "created_at"]
    )

    op.create_table(
        "certificates",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("course_id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("holder_name", sa.String(length=80), nullable=False),
        sa.Column("course_title", sa.String(length=200), nullable=False),
        sa.Column("criteria", postgresql.JSONB(), nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_certificates_user_id_users"), ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["course_id"], ["courses.id"], name=op.f("fk_certificates_course_id_courses"), ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_certificates")),
        sa.UniqueConstraint("user_id", "course_id", name=op.f("uq_certificates_user_course")),
        sa.UniqueConstraint("code", name=op.f("uq_certificates_code")),
    )
    op.create_index(op.f("ix_certificates_course_id"), "certificates", ["course_id"])


def downgrade() -> None:
    op.drop_table("certificates")
    op.drop_table("rate_limit_hits")
