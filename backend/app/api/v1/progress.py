import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import User
from app.schemas.curriculum import LessonProgressRead, TimeRequest
from app.schemas.progress import ProgressSummary
from app.services import progress_service

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("/summary", response_model=ProgressSummary)
def read_summary(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> ProgressSummary:
    return progress_service.get_summary(db, user.id)


@router.post("/lessons/{lesson_id}/start", response_model=LessonProgressRead)
def start_lesson(
    lesson_id: uuid.UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> LessonProgressRead:
    return progress_service.start_lesson(db, user.id, lesson_id)


@router.post("/lessons/{lesson_id}/time", response_model=LessonProgressRead)
def add_time(
    lesson_id: uuid.UUID,
    payload: TimeRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> LessonProgressRead:
    return progress_service.add_time(db, user.id, lesson_id, payload.seconds)


@router.post("/lessons/{lesson_id}/complete", response_model=LessonProgressRead)
def complete_lesson(
    lesson_id: uuid.UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> LessonProgressRead:
    return progress_service.complete_lesson(db, user.id, lesson_id)
