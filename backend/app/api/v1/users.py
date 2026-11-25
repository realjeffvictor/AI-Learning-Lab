import uuid

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api.deps import client_ip, get_current_user, get_db, require_roles
from app.models import User
from app.schemas.user import AdminUserUpdate, ProfileUpdate, UserPage, UserRead
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def read_me(user: User = Depends(get_current_user)) -> User:
    return user


@router.patch("/me/profile", response_model=UserRead)
def update_my_profile(
    payload: ProfileUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    return user_service.update_profile(db, user, payload.model_dump(exclude_unset=True))


@router.get("", response_model=UserPage)
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _admin: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
) -> UserPage:
    users, total = user_service.list_users(db, page, page_size)
    return UserPage(items=[UserRead.model_validate(u) for u in users], page=page, page_size=page_size, total=total)


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: uuid.UUID,
    payload: AdminUserUpdate,
    request: Request,
    admin: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
) -> User:
    return user_service.admin_update_user(
        db, admin, user_id, payload.model_dump(exclude_unset=True), client_ip(request)
    )
