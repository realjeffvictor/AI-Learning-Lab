import uuid
from datetime import date

from sqlalchemy import CheckConstraint, Date, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, CreatedAtMixin, TimestampMixin, UUIDPrimaryKeyMixin


class AIConversation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "ai_conversations"
    __table_args__ = (
        CheckConstraint(
            "assistant IN ('tutor', 'code', 'debug', 'architecture', 'testing', 'docs', 'review')",
            name="assistant_valid",
        ),
        Index("ix_ai_conversations_user_id_updated_at", "user_id", "updated_at"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    assistant: Mapped[str] = mapped_column(String(20))
    title: Mapped[str] = mapped_column(String(120))
    lesson_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("lessons.id", ondelete="SET NULL"))
    exercise_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("exercises.id", ondelete="SET NULL"))


class AIMessage(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    """created_at is set explicitly by the service (not the database clock) so a user message and its reply sort correctly."""

    __tablename__ = "ai_messages"
    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant')", name="role_valid"),
        CheckConstraint("mode IN ('hint', 'pair', 'generate', 'review')", name="mode_valid"),
        Index("ix_ai_messages_conversation_id_created_at", "conversation_id", "created_at"),
    )

    conversation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ai_conversations.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(10))
    mode: Mapped[str] = mapped_column(String(12))
    content: Mapped[str] = mapped_column(Text)


class AIUsageCounter(TimestampMixin, Base):
    __tablename__ = "ai_usage_counters"
    __table_args__ = (
        CheckConstraint("requests >= 0 AND tokens_in >= 0 AND tokens_out >= 0", name="non_negative"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    day: Mapped[date] = mapped_column(Date, primary_key=True)
    requests: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    tokens_in: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    tokens_out: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
