"""notifications, and managed_in_app flags for content edited in the app

Revision ID: 0006
Revises: 0005
Create Date: 2026-11-26
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    for table in ("lessons", "exercises", "projects"):
        op.add_column(table, sa.Column("managed_in_app", sa.Boolean(), server_default=sa.false(), nullable=False))

    op.create_table(
        "notifications",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("kind", sa.String(length=30), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("body", sa.String(length=500), server_default="", nullable=False),
        sa.Column("link", sa.String(length=200), nullable=True),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_notifications_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_notifications")),
    )
    op.create_index(op.f("ix_notifications_user_id_created_at"), "notifications", ["user_id", "created_at"])


def downgrade() -> None:
    op.drop_table("notifications")
    for table in ("projects", "exercises", "lessons"):
        op.drop_column(table, "managed_in_app")
