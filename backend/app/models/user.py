import uuid
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

ROLES = ("student", "instructor", "admin")
EXPERIENCE_LEVELS = ("beginner", "intermediate", "advanced")


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
        CheckConstraint("role IN ('student', 'instructor', 'admin')", name="role_valid"),
        CheckConstraint("email = lower(email)", name="email_lowercase"),
    )

    email: Mapped[str] = mapped_column(String(254))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="student", server_default="student")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true())
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    profile: Mapped["UserProfile"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan", passive_deletes=True, lazy="joined"
    )


class UserProfile(TimestampMixin, Base):
    __tablename__ = "user_profiles"
    __table_args__ = (
        CheckConstraint("experience_level IN ('beginner', 'intermediate', 'advanced')", name="experience_level_valid"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(80))
    bio: Mapped[str | None] = mapped_column(String(500))
    experience_level: Mapped[str] = mapped_column(String(20), default="beginner", server_default="beginner")

    user: Mapped[User] = relationship(back_populates="profile")
