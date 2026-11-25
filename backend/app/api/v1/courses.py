from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import User
from app.schemas.curriculum import CourseDetail, CourseSummary, EnrollmentRead, LessonDetail
from app.services import curriculum_service

router = APIRouter(prefix="/courses", tags=["curriculum"])


@router.get("", response_model=list[CourseSummary])
def list_courses(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[CourseSummary]:
    return curriculum_service.list_courses(db, user.id)


@router.get("/{course_slug}", response_model=CourseDetail)
def read_course(course_slug: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> CourseDetail:
    return curriculum_service.get_course(db, user.id, course_slug)


@router.get("/{course_slug}/modules/{module_slug}/lessons/{lesson_slug}", response_model=LessonDetail)
def read_lesson(
    course_slug: str,
    module_slug: str,
    lesson_slug: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> LessonDetail:
    return curriculum_service.get_lesson(db, user.id, course_slug, module_slug, lesson_slug)


@router.post("/{course_slug}/enrollment", response_model=EnrollmentRead)
def enroll(course_slug: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> EnrollmentRead:
    return curriculum_service.enroll(db, user.id, course_slug)
