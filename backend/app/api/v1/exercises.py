import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.api.rate_limit import user_rate_limit
from app.models import User
from app.schemas.assessment import ExercisePublic, MasteryRead, SubmissionCreate, SubmissionResult, SubmissionSummary
from app.services import assessment_service

router = APIRouter(tags=["exercises"])

submit_limit = user_rate_limit("submit", "rl_submit_per_hour", 3600)


@router.get("/lessons/{lesson_id}/exercises", response_model=list[ExercisePublic])
def list_exercises(
    lesson_id: uuid.UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[ExercisePublic]:
    return assessment_service.list_for_lesson(db, user.id, lesson_id)


@router.post(
    "/exercises/{exercise_id}/submissions",
    response_model=SubmissionResult,
    status_code=201,
    dependencies=[Depends(submit_limit)],
)
def submit_exercise(
    exercise_id: uuid.UUID,
    payload: SubmissionCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SubmissionResult:
    return assessment_service.submit(db, user.id, exercise_id, payload.answer)


@router.get("/exercises/{exercise_id}/submissions", response_model=list[SubmissionSummary])
def read_history(
    exercise_id: uuid.UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[SubmissionSummary]:
    return assessment_service.history(db, user.id, exercise_id)


@router.get("/assessments/mastery", response_model=list[MasteryRead])
def read_mastery(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[MasteryRead]:
    return assessment_service.mastery(db, user.id)
