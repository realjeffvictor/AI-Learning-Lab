import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

LessonStatus = Literal["published", "planned"]
ProgressStatus = Literal["not_started", "in_progress", "completed"]
CourseKind = Literal["stage", "track"]


class ConceptRead(BaseModel):
    slug: str
    name: str
    category: Literal["A", "B", "C"]


class LessonSummary(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    summary: str
    position: int
    estimated_minutes: int
    status: LessonStatus
    principles: list[str]
    progress: ProgressStatus


class ModuleRead(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    summary: str
    position: int
    status: LessonStatus
    lessons: list[LessonSummary]


class CourseSummary(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    summary: str
    kind: CourseKind
    stage_number: int | None
    position: int
    module_count: int
    published_lesson_count: int
    planned_lesson_count: int
    completed_lesson_count: int
    enrolled: bool


class CourseDetail(CourseSummary):
    modules: list[ModuleRead]


class LessonLink(BaseModel):
    module_slug: str
    slug: str
    title: str


class LessonProgressRead(BaseModel):
    status: ProgressStatus
    time_spent_seconds: int
    completed_at: datetime | None


class LessonDetail(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    summary: str
    estimated_minutes: int
    status: LessonStatus
    objectives: list[str]
    principles: list[str]
    content_md: str | None
    concepts: list[ConceptRead]
    course_slug: str
    course_title: str
    module_slug: str
    module_title: str
    progress: LessonProgressRead
    previous: LessonLink | None
    next: LessonLink | None


class EnrollmentRead(BaseModel):
    course_slug: str
    enrolled_at: datetime


class TimeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    seconds: int = Field(ge=1, le=120)
