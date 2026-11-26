from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import User
from app.schemas.project import AchievementRead
from app.services import achievement_service

router = APIRouter(prefix="/achievements", tags=["achievements"])


@router.get("", response_model=list[AchievementRead])
def list_achievements(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[AchievementRead]:
    """Also records newly earned achievements. Repeating the call changes nothing."""
    return achievement_service.list_for_user(db, user.id)
