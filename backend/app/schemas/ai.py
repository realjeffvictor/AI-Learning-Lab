import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.assessment import ConceptResult, Recommendation

AssistantId = Literal["tutor", "code", "debug", "architecture", "testing", "docs", "review"]
ModeId = Literal["independent", "hint", "pair", "generate", "review"]
StoredModeId = Literal["hint", "pair", "generate", "review"]

MAX_MESSAGE_CHARS = 4000
MAX_CODE_CHARS = 8000


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    assistant: AssistantId
    mode: ModeId
    message: str = Field(min_length=1, max_length=MAX_MESSAGE_CHARS)
    conversation_id: uuid.UUID | None = None
    lesson_id: uuid.UUID | None = None
    exercise_id: uuid.UUID | None = None
    code: str | None = Field(default=None, max_length=MAX_CODE_CHARS)

    @field_validator("message")
    @classmethod
    def _not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Message cannot be blank.")
        return value.strip()


class UsageRead(BaseModel):
    requests_used: int
    requests_limit: int
    tokens_used: int
    tokens_limit: int


class AIStatus(BaseModel):
    enabled: bool
    model: str | None
    usage: UsageRead


class ChatResponse(BaseModel):
    conversation_id: uuid.UUID
    assistant: AssistantId
    mode: StoredModeId
    reply: str
    usage: UsageRead


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    role: Literal["user", "assistant"]
    mode: StoredModeId
    content: str
    created_at: datetime


class ConversationSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    assistant: AssistantId
    title: str
    updated_at: datetime


class ConversationDetail(BaseModel):
    id: uuid.UUID
    assistant: AssistantId
    title: str
    messages: list[MessageRead]


class StudyPlanResponse(BaseModel):
    reply: str
    weak_concepts: list[ConceptResult]
    recommendations: list[Recommendation]
    usage: UsageRead
