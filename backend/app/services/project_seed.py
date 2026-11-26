"""Writes validated projects into the database. Safe to run repeatedly; never deletes."""
import uuid
from dataclasses import dataclass, field

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models import Concept, Course, Project, ProjectConcept
from app.services.curriculum_loader import CurriculumError
from app.services.curriculum_seed import _apply
from app.services.project_loader import ProjectData


def _zero() -> dict[str, int]:
    return {"projects": 0}


@dataclass
class ProjectSeedReport:
    created: dict[str, int] = field(default_factory=_zero)
    updated: dict[str, int] = field(default_factory=_zero)
    orphans: list[str] = field(default_factory=list)


def seed_projects(session: Session, projects: tuple[ProjectData, ...]) -> ProjectSeedReport:
    report = ProjectSeedReport()
    concepts = {c.slug: c.id for c in session.scalars(select(Concept))}
    course_ids = {slug: course_id for slug, course_id in session.execute(select(Course.slug, Course.id)).all()}

    positions: dict[str, int] = {}
    wanted: set[tuple[uuid.UUID, str]] = set()
    for item in projects:
        course_id = course_ids.get(item.course_slug)
        if course_id is None:
            raise CurriculumError(f"projects/{item.course_slug}: course is not in the database; seed the curriculum first")
        positions[item.course_slug] = positions.get(item.course_slug, 0) + 1
        values = {
            "title": item.title,
            "summary": item.summary,
            "kind": item.kind,
            "position": positions[item.course_slug],
            "brief_md": item.brief_md,
            "requirements": [{"id": rid, "text": text} for rid, text in item.requirements],
        }
        existing = session.scalar(select(Project).where(Project.course_id == course_id, Project.slug == item.slug))
        if existing is not None and existing.managed_in_app:
            wanted.add((course_id, item.slug))
            report.orphans.append(f"project {item.slug} (edited in the app; the file was not applied)")
            continue
        changed = False
        if existing is None:
            project = Project(course_id=course_id, slug=item.slug, **values)
            session.add(project)
            report.created["projects"] += 1
        else:
            project = existing
            changed = _apply(project, values)
        session.flush()
        wanted.add((course_id, item.slug))

        wanted_ids = set()
        for slug in item.concepts:
            if slug not in concepts:
                raise CurriculumError(f"{item.slug}: concept '{slug}' is not in the database; seed the curriculum first")
            wanted_ids.add(concepts[slug])
        current = set(session.scalars(select(ProjectConcept.concept_id).where(ProjectConcept.project_id == project.id)))
        for concept_id in wanted_ids - current:
            session.add(ProjectConcept(project_id=project.id, concept_id=concept_id))
            changed = True
        stale = current - wanted_ids
        if stale:
            session.execute(
                delete(ProjectConcept).where(ProjectConcept.project_id == project.id, ProjectConcept.concept_id.in_(stale))
            )
            changed = True
        if changed and existing is not None:
            report.updated["projects"] += 1
    session.flush()

    for course_id, slug in session.execute(select(Project.course_id, Project.slug)).all():
        if (course_id, slug) not in wanted:
            report.orphans.append(f"project {slug}")
    return report
