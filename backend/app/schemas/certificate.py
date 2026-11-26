from datetime import datetime

from pydantic import BaseModel


class CertRequirement(BaseModel):
    key: str
    label: str
    done: int
    total: int


class CertificateRead(BaseModel):
    code: str
    course_slug: str
    course_title: str
    holder_name: str
    issued_at: datetime


class CertificateStatus(BaseModel):
    course_slug: str
    course_title: str
    eligible: bool
    message: str | None
    requirements: list[CertRequirement]
    certificate: CertificateRead | None


class PublicCertificate(BaseModel):
    """What anyone with the code may see. No email address, no user id."""

    valid: bool
    holder_name: str
    course_title: str
    issued_at: datetime
