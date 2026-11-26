import json
import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.assessment import MasteryRead
from app.schemas.curriculum import CourseSummary
from app.schemas.project import ProjectKind, ProjectSummary, Requirement
from app.schemas.user import Role, UserRead

LessonState = Literal["published", "planned"]
PrincipleLetter = Literal["U", "D", "B", "V", "O"]
ExerciseKind = Literal["code", "quiz", "puzzle"]


# ------------------------------------------------------------------ analytics
class EnrollmentCount(BaseModel):
    course_slug: str
    course_title: str
    enrolled: int


class LessonCompletion(BaseModel):
    course_slug: str
    module_slug: str
    lesson_slug: str
    title: str
    completed: int


class ExerciseStat(BaseModel):
    exercise_id: uuid.UUID
    title: str
    kind: ExerciseKind
    lesson_title: str
    attempts: int
    learners: int
    passed_learners: int


class AIUsageStat(BaseModel):
    requests_today: int
    requests_7d: int
    tokens_7d: int


class Overview(BaseModel):
    users_by_role: dict[str, int]
    active_learners_7d: int
    pending_reviews: int
    enrollments: list[EnrollmentCount]
    top_lessons: list[LessonCompletion]
    exercises: list[ExerciseStat]
    ai: AIUsageStat


# ------------------------------------------------------------------ students
class StudentRow(BaseModel):
    id: uuid.UUID
    email: str
    display_name: str
    role: Role
    is_active: bool
    created_at: datetime
    lessons_completed: int
    enrollments: int
    last_active_at: datetime | None


class StudentPage(BaseModel):
    items: list[StudentRow]
    page: int
    page_size: int
    total: int


class StudentDetail(BaseModel):
    user: UserRead
    lessons_completed: int
    time_spent_seconds: int
    exercise_attempts: int
    exercises_passed: int
    courses: list[CourseSummary]
    projects: list[ProjectSummary]
    mastery: list[MasteryRead]


# ------------------------------------------------------------------ content tree
class ContentLesson(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    status: LessonState
    managed_in_app: bool
    exercise_count: int


class ContentModule(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    lessons: list[ContentLesson]


class ContentProject(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    kind: ProjectKind
    managed_in_app: bool


class ContentCourse(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    kind: Literal["stage", "track"]
    modules: list[ContentModule]
    projects: list[ContentProject]


class ContentTree(BaseModel):
    courses: list[ContentCourse]


class ConceptOption(BaseModel):
    slug: str
    name: str
    category: Literal["A", "B", "C"]


# ------------------------------------------------------------------ lessons
class LessonWrite(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    summary: str = Field(default="", max_length=500)
    minutes: int = Field(ge=1, le=240)
    objectives: list[str] = Field(default_factory=list, max_length=8)
    principles: list[PrincipleLetter] = Field(default_factory=list, max_length=5)
    concepts: list[str] = Field(default_factory=list, max_length=12)
    content_md: str | None = Field(default=None, max_length=100_000)

    @field_validator("title")
    @classmethod
    def _title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Title cannot be blank.")
        return value

    @field_validator("objectives")
    @classmethod
    def _objectives(cls, value: list[str]) -> list[str]:
        cleaned = [item.strip() for item in value]
        if any(not item or len(item) > 200 for item in cleaned):
            raise ValueError("Each objective must be 1 to 200 characters.")
        return cleaned

    @field_validator("principles", "concepts")
    @classmethod
    def _unique(cls, value: list) -> list:
        if len(set(value)) != len(value):
            raise ValueError("Remove duplicates.")
        return value


class LessonCreate(LessonWrite):
    slug: str = Field(min_length=1, max_length=80)


class LessonEdit(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    summary: str
    minutes: int
    status: LessonState
    objectives: list[str]
    principles: list[str]
    concepts: list[str]
    content_md: str | None
    module_id: uuid.UUID
    module_slug: str
    module_title: str
    course_slug: str
    course_title: str
    managed_in_app: bool


# ------------------------------------------------------------------ exercises
class ExerciseWrite(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    instructions_md: str = Field(min_length=1, max_length=5000)
    pass_score: int = Field(ge=1, le=100)
    concepts: list[str] = Field(min_length=1, max_length=8)
    definition: dict[str, Any]

    @field_validator("title", "instructions_md")
    @classmethod
    def _not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank.")
        return value

    @field_validator("concepts")
    @classmethod
    def _unique(cls, value: list[str]) -> list[str]:
        if len(set(value)) != len(value):
            raise ValueError("Remove duplicate concepts.")
        return value

    @field_validator("definition")
    @classmethod
    def _small(cls, value: dict[str, Any]) -> dict[str, Any]:
        if len(json.dumps(value)) > 100_000:
            raise ValueError("The definition is too large.")
        return value


class ExerciseCreate(ExerciseWrite):
    slug: str = Field(min_length=1, max_length=40)
    kind: ExerciseKind


class ExerciseEdit(BaseModel):
    id: uuid.UUID
    lesson_id: uuid.UUID
    lesson_title: str
    slug: str
    title: str
    kind: ExerciseKind
    instructions_md: str
    pass_score: int
    concepts: list[str]
    definition: dict[str, Any]
    attempts: int
    managed_in_app: bool


# ------------------------------------------------------------------ projects
class ProjectWrite(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    summary: str = Field(default="", max_length=500)
    brief_md: str = Field(min_length=1, max_length=50_000)

    @field_validator("title", "brief_md")
    @classmethod
    def _not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank.")
        return value


class ProjectEdit(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    summary: str
    kind: ProjectKind
    course_slug: str
    course_title: str
    brief_md: str
    requirements: list[Requirement]
    managed_in_app: bool
