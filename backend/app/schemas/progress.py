from typing import Literal

from pydantic import BaseModel

from app.schemas.curriculum import CourseSummary


class CompetencyRead(BaseModel):
    slug: str
    name: str
    category: Literal["A", "B", "C"]
    lessons_completed: int


class UpNext(BaseModel):
    reason: Literal["continue", "start"]
    course_slug: str
    course_title: str
    module_slug: str
    lesson_slug: str
    lesson_title: str


class ProgressSummary(BaseModel):
    lessons_completed: int
    time_spent_seconds: int
    courses: list[CourseSummary]
    competencies: list[CompetencyRead]
    up_next: UpNext | None
