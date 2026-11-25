import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from app.schemas.curriculum import ConceptRead

ExerciseKind = Literal["code", "quiz", "puzzle"]


class ExercisePublic(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    kind: ExerciseKind
    position: int
    instructions_md: str
    pass_score: int
    concepts: list[ConceptRead]
    definition: dict[str, Any]
    attempts: int
    best_score: int | None
    passed: bool


class SubmissionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answer: dict[str, Any]


class FeedbackItem(BaseModel):
    id: str
    correct: bool
    message: str | None = None
    correct_index: int | None = None


class ConceptResult(BaseModel):
    slug: str
    name: str
    correct: int
    total: int


class Recommendation(BaseModel):
    type: Literal["lesson", "resource"]
    concept_slug: str
    concept_name: str
    title: str
    course_slug: str | None = None
    module_slug: str | None = None
    lesson_slug: str | None = None
    url: str | None = None
    resource_kind: str | None = None
    is_open_source: bool | None = None


class SubmissionResult(BaseModel):
    id: uuid.UUID
    score: int
    passed: bool
    pass_score: int
    attempt_number: int
    feedback: list[FeedbackItem]
    concept_results: list[ConceptResult]
    recommendations: list[Recommendation]
    created_at: datetime


class SubmissionSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    score: int
    passed: bool
    created_at: datetime


class MasteryRead(BaseModel):
    slug: str
    name: str
    category: Literal["A", "B", "C"]
    correct: int
    total: int
