import uuid

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import client_ip, get_current_user, get_db
from app.models import User
from app.schemas.project import ProjectDetail, ProjectSummary, SubmissionDraft, SubmissionRead
from app.services import project_service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectSummary])
def list_projects(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[ProjectSummary]:
    return project_service.list_projects(db, user.id)


@router.put("/{project_id}/submission", response_model=SubmissionRead)
def save_draft(
    project_id: uuid.UUID,
    payload: SubmissionDraft,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SubmissionRead:
    return project_service.save_draft(db, user.id, project_id, payload.model_dump(exclude_unset=True))


@router.post("/{project_id}/submission/submit", response_model=SubmissionRead)
def submit_project(
    project_id: uuid.UUID,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SubmissionRead:
    return project_service.submit(db, user.id, project_id, client_ip(request))


@router.get("/{course_slug}/{project_slug}", response_model=ProjectDetail)
def read_project(
    course_slug: str, project_slug: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> ProjectDetail:
    return project_service.get_project(db, user.id, course_slug, project_slug)
