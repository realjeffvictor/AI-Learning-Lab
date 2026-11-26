import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.project_rules import MAX_DOCUMENTATION_CHARS, MAX_REFLECTION_CHARS, normalize_repo_url
from app.schemas.curriculum import ConceptRead

ProjectKind = Literal["build", "architecture", "code_review"]
SubmissionStatus = Literal["draft", "submitted", "approved", "changes_requested"]
ProjectStatus = Literal["not_started", "draft", "submitted", "approved", "changes_requested"]
Outcome = Literal["approved", "changes_requested"]


class Requirement(BaseModel):
    id: str
    text: str


class ProjectSummary(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    summary: str
    kind: ProjectKind
    course_slug: str
    course_title: str
    status: ProjectStatus
    requirements_count: int


class SubmissionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: SubmissionStatus
    repo_url: str | None
    documentation_md: str
    reflection_md: str
    requirement_checks: dict[str, bool]
    submitted_at: datetime | None
    updated_at: datetime


class ReviewRead(BaseModel):
    id: uuid.UUID
    outcome: Outcome
    rubric_scores: dict[str, int]
    feedback: str
    created_at: datetime
    reviewer_name: str | None


class ProjectDetail(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    summary: str
    kind: ProjectKind
    course_slug: str
    course_title: str
    brief_md: str
    requirements: list[Requirement]
    requires_repo: bool
    concepts: list[ConceptRead]
    min_documentation_chars: int
    min_reflection_chars: int
    submission: SubmissionRead | None
    reviews: list[ReviewRead]


class SubmissionDraft(BaseModel):
    """Partial update: only the fields the client sends are changed."""

    model_config = ConfigDict(extra="forbid")

    repo_url: str | None = Field(default=None, max_length=200)
    documentation_md: str | None = Field(default=None, max_length=MAX_DOCUMENTATION_CHARS)
    reflection_md: str | None = Field(default=None, max_length=MAX_REFLECTION_CHARS)
    requirement_checks: dict[str, bool] | None = None

    @field_validator("repo_url")
    @classmethod
    def _repo(cls, value: str | None) -> str | None:
        return normalize_repo_url(value)


class RubricScores(BaseModel):
    model_config = ConfigDict(extra="forbid")

    understanding: int = Field(ge=1, le=4)
    implementation: int = Field(ge=1, le=4)
    verification: int = Field(ge=1, le=4)
    ownership: int = Field(ge=1, le=4)


class ReviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    outcome: Outcome
    rubric_scores: RubricScores
    feedback: str = Field(max_length=4000)

    @field_validator("feedback")
    @classmethod
    def _feedback(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 10:
            raise ValueError("Write at least a sentence of feedback.")
        return value


class QueueItem(BaseModel):
    submission_id: uuid.UUID
    project_title: str
    project_kind: ProjectKind
    course_slug: str
    course_title: str
    learner_name: str
    learner_email: str
    submitted_at: datetime


class QueuePage(BaseModel):
    items: list[QueueItem]
    page: int
    page_size: int
    total: int


class ReviewDetail(BaseModel):
    submission: SubmissionRead
    project_title: str
    project_kind: ProjectKind
    course_slug: str
    course_title: str
    brief_md: str
    requirements: list[Requirement]
    learner_name: str
    learner_email: str
    reviews: list[ReviewRead]


class AchievementRead(BaseModel):
    key: str
    title: str
    description: str
    earned: bool
    earned_at: datetime | None
