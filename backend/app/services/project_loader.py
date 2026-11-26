"""Reads projects from curriculum/projects/<course-slug>/<project-slug>.json plus a matching .md brief. No database."""
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.services.curriculum_loader import (
    CurriculumData,
    CurriculumError,
    _object,
    _read_json,
    _string,
    _string_list,
)
from app.services.exercise_loader import IDENT, _ident

PROJECT_KINDS = ("build", "architecture", "code_review")
MAX_BRIEF_BYTES = 50_000


@dataclass(frozen=True)
class ProjectData:
    course_slug: str
    slug: str
    title: str
    summary: str
    kind: str
    brief_md: str
    requirements: tuple[tuple[str, str], ...]  # (id, text)
    concepts: tuple[str, ...]


def _load_project(path: Path, root: Path, course_slug: str, concept_slugs: set[str]) -> ProjectData:
    where = str(path.relative_to(root))
    slug = path.stem
    if not IDENT.fullmatch(slug):
        raise CurriculumError(f"{where}: the file name must match {IDENT.pattern}")
    item = _object(_read_json(path), where)

    kind = item.get("kind")
    if kind not in PROJECT_KINDS:
        raise CurriculumError(f"{where}: 'kind' must be one of {', '.join(PROJECT_KINDS)}")

    concepts = _string_list(item, "concepts", where, max_items=8, max_len=80)
    if not concepts:
        raise CurriculumError(f"{where}: at least one concept is required")
    for concept in concepts:
        if concept not in concept_slugs:
            raise CurriculumError(f"{where}: unknown concept '{concept}'")

    raw = item.get("requirements")
    if not isinstance(raw, list) or not 1 <= len(raw) <= 12:
        raise CurriculumError(f"{where}: 'requirements' must be a list of 1 to 12 requirements")
    seen: set[str] = set()
    requirements: list[tuple[str, str]] = []
    for index, entry in enumerate(raw):
        w = f"{where} requirements[{index}]"
        requirement = _object(entry, w)
        rid = _ident(requirement, "id", w)
        if rid in seen:
            raise CurriculumError(f"{w}: duplicate requirement id '{rid}'")
        seen.add(rid)
        requirements.append((rid, _string(requirement, "text", w, max_len=300)))

    brief_path = path.with_suffix(".md")
    if not brief_path.is_file():
        raise CurriculumError(f"{where}: missing brief file {brief_path.name}")
    if brief_path.stat().st_size > MAX_BRIEF_BYTES:
        raise CurriculumError(f"{brief_path.relative_to(root)}: file is larger than {MAX_BRIEF_BYTES} bytes")
    brief = brief_path.read_text(encoding="utf-8").strip()
    if not brief:
        raise CurriculumError(f"{brief_path.relative_to(root)}: file is empty")

    return ProjectData(
        course_slug=course_slug,
        slug=slug,
        title=_string(item, "title", where, max_len=200),
        summary=_string(item, "summary", where, max_len=500, required=False),
        kind=kind,
        brief_md=brief,
        requirements=tuple(requirements),
        concepts=concepts,
    )


def load_projects(root: Path, curriculum: CurriculumData) -> tuple[ProjectData, ...]:
    base = root / "projects"
    if not base.is_dir():
        return ()
    course_slugs = {course.slug for course in curriculum.courses}
    concept_slugs = {concept.slug for concept in curriculum.concepts}

    projects: list[ProjectData] = []
    for course_dir in sorted(p for p in base.iterdir() if p.is_dir()):
        if course_dir.name not in course_slugs:
            raise CurriculumError(f"{course_dir.relative_to(root)}: no course with this slug")
        json_files = sorted(course_dir.glob("*.json"))
        stems = {path.stem for path in json_files}
        for brief in sorted(course_dir.glob("*.md")):
            if brief.stem not in stems:
                raise CurriculumError(f"{brief.relative_to(root)}: brief has no matching .json file")
        for path in json_files:
            projects.append(_load_project(path, root, course_dir.name, concept_slugs))
    return tuple(projects)
