import re
import secrets
import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.security import utcnow
from app.models import Certificate, Course, User
from app.repositories import audit_repository, certificate_repository as repo, curriculum_repository
from app.schemas.certificate import CertificateRead, CertificateStatus, CertRequirement, PublicCertificate
from app.services import notification_service

CODE_PATTERN = re.compile(r"^[A-Za-z0-9_-]{8,64}$")


def _requirements(session: Session, user_id: uuid.UUID, course_id: uuid.UUID) -> list[CertRequirement]:
    lessons = repo.published_lesson_ids(session, course_id)
    exercises = repo.server_graded_exercise_ids(session, course_id)
    projects = repo.project_ids(session, course_id)
    return [
        CertRequirement(
            key="lessons",
            label="Complete every written lesson",
            done=len(repo.completed_among(session, user_id, lessons)),
            total=len(lessons),
        ),
        CertRequirement(
            key="exercises",
            label="Pass every quiz and puzzle",
            done=len(repo.passed_among(session, user_id, exercises)),
            total=len(exercises),
        ),
        CertRequirement(
            key="projects",
            label="Have every project approved by a reviewer",
            done=len(repo.approved_among(session, user_id, projects)),
            total=len(projects),
        ),
    ]


def _blocker(requirements: list[CertRequirement]) -> str | None:
    by_key = {item.key: item for item in requirements}
    if by_key["projects"].total == 0:
        return "This course has no reviewed project yet, so it cannot issue a certificate."
    if by_key["lessons"].total == 0:
        return "This course has no written lessons yet."
    missing = [item.label.lower() for item in requirements if item.done < item.total]
    return ("Still to do: " + "; ".join(missing) + ".") if missing else None


def _read(certificate: Certificate, course: Course) -> CertificateRead:
    return CertificateRead(
        code=certificate.code,
        course_slug=course.slug,
        course_title=certificate.course_title,
        holder_name=certificate.holder_name,
        issued_at=certificate.issued_at,
    )


def list_status(session: Session, user_id: uuid.UUID) -> list[CertificateStatus]:
    issued = repo.list_for_user(session, user_id)
    result: list[CertificateStatus] = []
    for course in curriculum_repository.list_courses(session):
        requirements = _requirements(session, user_id, course.id)
        blocker = _blocker(requirements)
        certificate = issued.get(course.id)
        result.append(
            CertificateStatus(
                course_slug=course.slug,
                course_title=course.title,
                eligible=blocker is None,
                message=None if certificate or blocker is None else blocker,
                requirements=requirements,
                certificate=_read(certificate, course) if certificate else None,
            )
        )
    return result


def issue(session: Session, user: User, course_slug: str) -> CertificateRead:
    course = curriculum_repository.get_course_basic(session, course_slug)
    if course is None:
        raise AppError(404, "course_not_found", "Course not found.")
    existing = repo.get_for_user(session, user.id, course.id)
    if existing is not None:
        return _read(existing, course)

    requirements = _requirements(session, user.id, course.id)
    blocker = _blocker(requirements)
    if blocker is not None:
        raise AppError(409, "not_eligible", blocker)

    certificate = Certificate(
        user_id=user.id,
        course_id=course.id,
        code=secrets.token_urlsafe(12),
        holder_name=user.profile.display_name,
        course_title=course.title,
        criteria={item.key: item.done for item in requirements},
        issued_at=utcnow(),
    )
    session.add(certificate)
    try:
        session.flush()
    except IntegrityError:  # two simultaneous requests: keep the one that won
        session.rollback()
        winner = repo.get_for_user(session, user.id, course.id)
        assert winner is not None
        return _read(winner, course)
    notification_service.create(
        session,
        user.id,
        "certificate",
        f"Certificate issued: {course.title}",
        "Share the verification link from the Progress page.",
        "/progress",
    )
    audit_repository.record(session, "certificate.issued", actor_user_id=user.id, details={"course": course.slug})
    session.commit()
    return _read(certificate, course)


def verify(session: Session, code: str) -> PublicCertificate:
    certificate = repo.get_by_code(session, code) if CODE_PATTERN.fullmatch(code) else None
    if certificate is None:
        raise AppError(404, "certificate_not_found", "No certificate matches this code.")
    return PublicCertificate(
        valid=True,
        holder_name=certificate.holder_name,
        course_title=certificate.course_title,
        issued_at=certificate.issued_at,
    )
