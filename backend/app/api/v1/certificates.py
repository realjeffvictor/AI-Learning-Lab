from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.api.rate_limit import ip_rate_limit, user_rate_limit
from app.models import User
from app.schemas.certificate import CertificateRead, CertificateStatus, PublicCertificate
from app.services import certificate_service

router = APIRouter(prefix="/certificates", tags=["certificates"])

verify_limit = ip_rate_limit("cert-verify", "rl_verify_per_minute", 60)
issue_limit = user_rate_limit("cert-issue", "rl_submit_per_hour", 3600)


@router.get("", response_model=list[CertificateStatus])
def list_certificates(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[CertificateStatus]:
    return certificate_service.list_status(db, user.id)


@router.post("/{course_slug}", response_model=CertificateRead, dependencies=[Depends(issue_limit)])
def issue_certificate(
    course_slug: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> CertificateRead:
    return certificate_service.issue(db, user, course_slug)


@router.get("/verify/{code}", response_model=PublicCertificate, dependencies=[Depends(verify_limit)])
def verify_certificate(code: str, db: Session = Depends(get_db)) -> PublicCertificate:
    """Public: anyone holding the code can check it. Rate limited by IP."""
    return certificate_service.verify(db, code)
