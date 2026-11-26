import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Index, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin


class RateLimitHit(UUIDPrimaryKeyMixin, Base):
    """One row per counted request. Shared by every API process, so limits survive restarts and scaling."""

    __tablename__ = "rate_limit_hits"
    __table_args__ = (Index("ix_rate_limit_hits_bucket_key_created_at", "bucket", "key", "created_at"),)

    bucket: Mapped[str] = mapped_column(String(40))
    key: Mapped[str] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Certificate(UUIDPrimaryKeyMixin, Base):
    """Issued once per learner and course. The name and title are snapshots, so later edits do not change a certificate."""

    __tablename__ = "certificates"
    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="uq_certificates_user_course"),
        UniqueConstraint("code", name="uq_certificates_code"),
        Index("ix_certificates_course_id", "course_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="RESTRICT"))
    code: Mapped[str] = mapped_column(String(32))
    holder_name: Mapped[str] = mapped_column(String(80))
    course_title: Mapped[str] = mapped_column(String(200))
    criteria: Mapped[dict[str, Any]] = mapped_column(JSONB)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
