import uuid

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import User
from app.schemas.notification import NotificationList, UnreadCount
from app.services import notification_service

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=NotificationList)
def list_notifications(
    limit: int = Query(30, ge=1, le=100), user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> NotificationList:
    return notification_service.list_for_user(db, user.id, limit)


@router.get("/unread-count", response_model=UnreadCount)
def read_unread_count(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> UnreadCount:
    return UnreadCount(unread_count=notification_service.unread_count(db, user.id))


@router.post("/read-all", status_code=204)
def read_all(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Response:
    notification_service.mark_all_read(db, user.id)
    return Response(status_code=204)


@router.post("/{notification_id}/read", status_code=204)
def read_one(
    notification_id: uuid.UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> Response:
    notification_service.mark_read(db, user.id, notification_id)
    return Response(status_code=204)
