import uuid
from typing import Literal

from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy.orm import Session

from app.api.deps import client_ip, get_db, require_roles
from app.models import User
from app.schemas.curriculum import EnrollmentRead
from app.schemas.manage import (
    ConceptOption,
    ContentTree,
    ExerciseCreate,
    ExerciseEdit,
    ExerciseWrite,
    LessonCreate,
    LessonEdit,
    LessonWrite,
    Overview,
    ProjectEdit,
    ProjectWrite,
    StudentDetail,
    StudentPage,
)
from app.services import content_service, staff_service

router = APIRouter(prefix="/manage", tags=["manage"])

# The real permission check for everything under /manage. Frontend route guards are cosmetic.
staff = require_roles("instructor", "admin")


@router.get("/overview", response_model=Overview)
def read_overview(_staff: User = Depends(staff), db: Session = Depends(get_db)) -> Overview:
    return staff_service.overview(db)


@router.get("/students", response_model=StudentPage)
def list_students(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    q: str | None = Query(None, max_length=100),
    role: Literal["student", "instructor", "admin"] | None = Query(None),
    _staff: User = Depends(staff),
    db: Session = Depends(get_db),
) -> StudentPage:
    return staff_service.list_students(db, page, page_size, q, role)


@router.get("/students/{user_id}", response_model=StudentDetail)
def read_student(user_id: uuid.UUID, _staff: User = Depends(staff), db: Session = Depends(get_db)) -> StudentDetail:
    return staff_service.student_detail(db, user_id)


@router.put("/students/{user_id}/enrollments/{course_slug}", response_model=EnrollmentRead)
def enroll_student(
    user_id: uuid.UUID, course_slug: str, request: Request,
    actor: User = Depends(staff), db: Session = Depends(get_db),
) -> EnrollmentRead:
    return staff_service.enroll(db, actor, user_id, course_slug, client_ip(request))


@router.delete("/students/{user_id}/enrollments/{course_slug}", status_code=204)
def unenroll_student(
    user_id: uuid.UUID, course_slug: str, request: Request,
    actor: User = Depends(staff), db: Session = Depends(get_db),
) -> Response:
    staff_service.unenroll(db, actor, user_id, course_slug, client_ip(request))
    return Response(status_code=204)


@router.get("/content", response_model=ContentTree)
def read_content(_staff: User = Depends(staff), db: Session = Depends(get_db)) -> ContentTree:
    return content_service.get_tree(db)


@router.get("/concepts", response_model=list[ConceptOption])
def read_concepts(_staff: User = Depends(staff), db: Session = Depends(get_db)) -> list[ConceptOption]:
    return content_service.list_concepts(db)


@router.get("/lessons/{lesson_id}", response_model=LessonEdit)
def read_lesson(lesson_id: uuid.UUID, _staff: User = Depends(staff), db: Session = Depends(get_db)) -> LessonEdit:
    return content_service.get_lesson(db, lesson_id)


@router.post("/modules/{module_id}/lessons", response_model=LessonEdit, status_code=201)
def create_lesson(
    module_id: uuid.UUID, payload: LessonCreate, request: Request,
    actor: User = Depends(staff), db: Session = Depends(get_db),
) -> LessonEdit:
    return content_service.create_lesson(db, actor, module_id, payload, client_ip(request))


@router.put("/lessons/{lesson_id}", response_model=LessonEdit)
def update_lesson(
    lesson_id: uuid.UUID, payload: LessonWrite, request: Request,
    actor: User = Depends(staff), db: Session = Depends(get_db),
) -> LessonEdit:
    return content_service.update_lesson(db, actor, lesson_id, payload, client_ip(request))


@router.get("/lessons/{lesson_id}/exercises", response_model=list[ExerciseEdit])
def list_exercises(
    lesson_id: uuid.UUID, _staff: User = Depends(staff), db: Session = Depends(get_db)
) -> list[ExerciseEdit]:
    return content_service.list_exercises(db, lesson_id)


@router.post("/lessons/{lesson_id}/exercises", response_model=ExerciseEdit, status_code=201)
def create_exercise(
    lesson_id: uuid.UUID, payload: ExerciseCreate, request: Request,
    actor: User = Depends(staff), db: Session = Depends(get_db),
) -> ExerciseEdit:
    return content_service.create_exercise(db, actor, lesson_id, payload, client_ip(request))


@router.get("/exercises/{exercise_id}", response_model=ExerciseEdit)
def read_exercise(exercise_id: uuid.UUID, _staff: User = Depends(staff), db: Session = Depends(get_db)) -> ExerciseEdit:
    return content_service.get_exercise(db, exercise_id)


@router.put("/exercises/{exercise_id}", response_model=ExerciseEdit)
def update_exercise(
    exercise_id: uuid.UUID, payload: ExerciseWrite, request: Request,
    actor: User = Depends(staff), db: Session = Depends(get_db),
) -> ExerciseEdit:
    return content_service.update_exercise(db, actor, exercise_id, payload, client_ip(request))


@router.delete("/exercises/{exercise_id}", status_code=204)
def delete_exercise(
    exercise_id: uuid.UUID, request: Request, actor: User = Depends(staff), db: Session = Depends(get_db)
) -> Response:
    content_service.delete_exercise(db, actor, exercise_id, client_ip(request))
    return Response(status_code=204)


@router.get("/projects/{project_id}", response_model=ProjectEdit)
def read_project(project_id: uuid.UUID, _staff: User = Depends(staff), db: Session = Depends(get_db)) -> ProjectEdit:
    return content_service.get_project(db, project_id)


@router.put("/projects/{project_id}", response_model=ProjectEdit)
def update_project(
    project_id: uuid.UUID, payload: ProjectWrite, request: Request,
    actor: User = Depends(staff), db: Session = Depends(get_db),
) -> ProjectEdit:
    return content_service.update_project(db, actor, project_id, payload, client_ip(request))
