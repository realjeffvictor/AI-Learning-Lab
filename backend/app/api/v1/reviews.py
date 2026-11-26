import uuid

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api.deps import client_ip, get_db, require_roles
from app.models import User
from app.schemas.project import QueuePage, ReviewDetail, ReviewRequest
from app.services import review_service

router = APIRouter(prefix="/reviews", tags=["reviews"])

# The real permission check. The frontend hides these pages from students, but this is what enforces it.
staff = require_roles("instructor", "admin")


@router.get("/queue", response_model=QueuePage)
def read_queue(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _staff: User = Depends(staff),
    db: Session = Depends(get_db),
) -> QueuePage:
    return review_service.queue(db, page, page_size)


@router.get("/submissions/{submission_id}", response_model=ReviewDetail)
def read_submission(
    submission_id: uuid.UUID, _staff: User = Depends(staff), db: Session = Depends(get_db)
) -> ReviewDetail:
    return review_service.get_detail(db, submission_id)


@router.post("/submissions/{submission_id}", response_model=ReviewDetail)
def post_review(
    submission_id: uuid.UUID,
    payload: ReviewRequest,
    request: Request,
    reviewer: User = Depends(staff),
    db: Session = Depends(get_db),
) -> ReviewDetail:
    return review_service.review(db, reviewer, submission_id, payload, client_ip(request))
