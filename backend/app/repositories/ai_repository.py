import uuid
from datetime import date, datetime

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.models import AIConversation, AIMessage, AIUsageCounter


def get_usage(session: Session, user_id: uuid.UUID, day: date) -> tuple[int, int]:
    """Returns (requests, total tokens) used on that UTC day."""
    row = session.execute(
        select(AIUsageCounter.requests, AIUsageCounter.tokens_in, AIUsageCounter.tokens_out).where(
            AIUsageCounter.user_id == user_id, AIUsageCounter.day == day
        )
    ).first()
    return (row.requests, row.tokens_in + row.tokens_out) if row else (0, 0)


def record_usage(session: Session, user_id: uuid.UUID, day: date, tokens_in: int, tokens_out: int) -> None:
    table = AIUsageCounter.__table__
    statement = pg_insert(AIUsageCounter).values(
        user_id=user_id, day=day, requests=1, tokens_in=tokens_in, tokens_out=tokens_out
    )
    session.execute(
        statement.on_conflict_do_update(
            index_elements=["user_id", "day"],
            set_={
                "requests": table.c.requests + 1,
                "tokens_in": table.c.tokens_in + tokens_in,
                "tokens_out": table.c.tokens_out + tokens_out,
                "updated_at": func.now(),
            },
        )
    )


def create_conversation(
    session: Session,
    user_id: uuid.UUID,
    assistant: str,
    title: str,
    lesson_id: uuid.UUID | None,
    exercise_id: uuid.UUID | None,
) -> AIConversation:
    conversation = AIConversation(
        user_id=user_id, assistant=assistant, title=title, lesson_id=lesson_id, exercise_id=exercise_id
    )
    session.add(conversation)
    session.flush()
    return conversation


def get_conversation(session: Session, user_id: uuid.UUID, conversation_id: uuid.UUID) -> AIConversation | None:
    """Always filtered by owner: a user can never reach another user's conversation."""
    return session.scalar(
        select(AIConversation).where(AIConversation.id == conversation_id, AIConversation.user_id == user_id)
    )


def list_conversations(session: Session, user_id: uuid.UUID, limit: int = 20) -> list[AIConversation]:
    return list(
        session.scalars(
            select(AIConversation)
            .where(AIConversation.user_id == user_id)
            .order_by(AIConversation.updated_at.desc(), AIConversation.id)
            .limit(limit)
        )
    )


def add_message(
    session: Session, conversation_id: uuid.UUID, role: str, mode: str, content: str, created_at: datetime
) -> AIMessage:
    message = AIMessage(conversation_id=conversation_id, role=role, mode=mode, content=content, created_at=created_at)
    session.add(message)
    return message


def recent_messages(session: Session, conversation_id: uuid.UUID, limit: int) -> list[AIMessage]:
    rows = session.scalars(
        select(AIMessage)
        .where(AIMessage.conversation_id == conversation_id)
        .order_by(AIMessage.created_at.desc(), AIMessage.id.desc())
        .limit(limit)
    )
    return list(reversed(list(rows)))


def all_messages(session: Session, conversation_id: uuid.UUID, limit: int = 200) -> list[AIMessage]:
    return list(
        session.scalars(
            select(AIMessage)
            .where(AIMessage.conversation_id == conversation_id)
            .order_by(AIMessage.created_at, AIMessage.id)
            .limit(limit)
        )
    )


def delete_conversation(session: Session, conversation: AIConversation) -> None:
    session.delete(conversation)  # messages go with it (ON DELETE CASCADE)
