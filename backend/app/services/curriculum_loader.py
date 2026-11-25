"""Reads the curriculum/ folder into validated, immutable data. Touches no database."""
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PRINCIPLE_LETTERS = ("U", "D", "B", "V", "O")
MAX_MARKDOWN_BYTES = 200_000


class CurriculumError(Exception):
    """The curriculum files are invalid. The message names the file and the problem."""


@dataclass(frozen=True)
class ConceptData:
    slug: str
    name: str
    category: str
    description: str


@dataclass(frozen=True)
class LessonData:
    slug: str
    title: str
    summary: str
    minutes: int
    principles: tuple[str, ...]
    objectives: tuple[str, ...]
    concepts: tuple[str, ...]
    content_md: str | None


@dataclass(frozen=True)
class ModuleData:
    slug: str
    title: str
    summary: str
    lessons: tuple[LessonData, ...]


@dataclass(frozen=True)
class CourseData:
    slug: str
    title: str
    summary: str
    kind: str
    stage_number: int | None
    modules: tuple[ModuleData, ...]


@dataclass(frozen=True)
class CurriculumData:
    concepts: tuple[ConceptData, ...]
    courses: tuple[CourseData, ...]


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise CurriculumError(f"{path}: file not found") from None
    except (OSError, ValueError) as exc:
        raise CurriculumError(f"{path}: cannot parse ({exc})") from None


def _object(value: Any, where: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise CurriculumError(f"{where}: expected an object")
    return value


def _string(obj: dict[str, Any], key: str, where: str, *, max_len: int, required: bool = True) -> str:
    value = obj.get(key)
    if value is None:
        if required:
            raise CurriculumError(f"{where}: '{key}' is required")
        return ""
    if not isinstance(value, str) or (required and not value.strip()):
        raise CurriculumError(f"{where}: '{key}' must be a non-empty string")
    if len(value) > max_len:
        raise CurriculumError(f"{where}: '{key}' is longer than {max_len} characters")
    return value.strip()


def _slug(obj: dict[str, Any], where: str) -> str:
    slug = _string(obj, "slug", where, max_len=80)
    if not SLUG_PATTERN.fullmatch(slug):
        raise CurriculumError(f"{where}: invalid slug '{slug}' (lowercase letters, digits and hyphens only)")
    return slug


def _string_list(obj: dict[str, Any], key: str, where: str, *, max_items: int, max_len: int) -> tuple[str, ...]:
    value = obj.get(key, [])
    if not isinstance(value, list) or len(value) > max_items:
        raise CurriculumError(f"{where}: '{key}' must be a list of at most {max_items} items")
    items: list[str] = []
    for entry in value:
        if not isinstance(entry, str) or not entry.strip() or len(entry) > max_len:
            raise CurriculumError(f"{where}: every item in '{key}' must be a non-empty string under {max_len} characters")
        items.append(entry.strip())
    return tuple(items)


def _load_concepts(root: Path) -> tuple[ConceptData, ...]:
    path = root / "concepts.json"
    raw = _read_json(path)
    if not isinstance(raw, list) or not raw:
        raise CurriculumError(f"{path}: expected a non-empty list")
    seen: set[str] = set()
    concepts: list[ConceptData] = []
    for index, entry in enumerate(raw):
        where = f"concepts.json[{index}]"
        item = _object(entry, where)
        slug = _slug(item, where)
        if slug in seen:
            raise CurriculumError(f"{where}: duplicate concept slug '{slug}'")
        seen.add(slug)
        category = _string(item, "category", where, max_len=1)
        if category not in ("A", "B", "C"):
            raise CurriculumError(f"{where}: category must be A, B or C")
        concepts.append(
            ConceptData(
                slug=slug,
                name=_string(item, "name", where, max_len=120),
                category=category,
                description=_string(item, "description", where, max_len=500, required=False),
            )
        )
    return tuple(concepts)


def _load_lesson(
    item: dict[str, Any], where: str, markdown_dir: Path, concept_slugs: set[str]
) -> LessonData:
    slug = _slug(item, where)
    where = f"{where} ('{slug}')"
    minutes = item.get("minutes", 10)
    if not isinstance(minutes, int) or isinstance(minutes, bool) or not 1 <= minutes <= 240:
        raise CurriculumError(f"{where}: 'minutes' must be an integer from 1 to 240")
    principles = _string_list(item, "principles", where, max_items=5, max_len=1)
    for letter in principles:
        if letter not in PRINCIPLE_LETTERS:
            raise CurriculumError(f"{where}: unknown principle '{letter}' (use U, D, B, V, O)")
    concepts = _string_list(item, "concepts", where, max_items=12, max_len=80)
    for concept in concepts:
        if concept not in concept_slugs:
            raise CurriculumError(f"{where}: unknown concept '{concept}'")

    content: str | None = None
    markdown_path = markdown_dir / f"{slug}.md"
    if markdown_path.is_file():
        if markdown_path.stat().st_size > MAX_MARKDOWN_BYTES:
            raise CurriculumError(f"{markdown_path}: file is larger than {MAX_MARKDOWN_BYTES} bytes")
        content = markdown_path.read_text(encoding="utf-8").strip()
        if not content:
            raise CurriculumError(f"{markdown_path}: file is empty")

    return LessonData(
        slug=slug,
        title=_string(item, "title", where, max_len=200),
        summary=_string(item, "summary", where, max_len=500, required=False),
        minutes=minutes,
        principles=principles,
        objectives=_string_list(item, "objectives", where, max_items=8, max_len=200),
        concepts=concepts,
        content_md=content,
    )


def _load_course(directory: Path, concept_slugs: set[str]) -> CourseData:
    path = directory / "course.json"
    where = f"{directory.name}/course.json"
    raw = _object(_read_json(path), where)
    slug = _slug(raw, where)
    kind = _string(raw, "kind", where, max_len=10)
    if kind not in ("stage", "track"):
        raise CurriculumError(f"{where}: kind must be 'stage' or 'track'")
    stage_number = raw.get("stage_number")
    if kind == "stage":
        if not isinstance(stage_number, int) or isinstance(stage_number, bool) or not 1 <= stage_number <= 9:
            raise CurriculumError(f"{where}: stage courses need an integer stage_number from 1 to 9")
    elif stage_number is not None:
        raise CurriculumError(f"{where}: track courses must not have a stage_number")

    modules_raw = raw.get("modules", [])
    if not isinstance(modules_raw, list):
        raise CurriculumError(f"{where}: 'modules' must be a list")
    module_slugs: set[str] = set()
    modules: list[ModuleData] = []
    for m_index, m_entry in enumerate(modules_raw):
        m_where = f"{where} modules[{m_index}]"
        module = _object(m_entry, m_where)
        module_slug = _slug(module, m_where)
        if module_slug in module_slugs:
            raise CurriculumError(f"{m_where}: duplicate module slug '{module_slug}'")
        module_slugs.add(module_slug)

        lessons_raw = module.get("lessons", [])
        if not isinstance(lessons_raw, list):
            raise CurriculumError(f"{m_where}: 'lessons' must be a list")
        markdown_dir = directory / module_slug
        lesson_slugs: set[str] = set()
        lessons: list[LessonData] = []
        for l_index, l_entry in enumerate(lessons_raw):
            lesson = _load_lesson(
                _object(l_entry, f"{m_where} lessons[{l_index}]"),
                f"{m_where} lessons[{l_index}]",
                markdown_dir,
                concept_slugs,
            )
            if lesson.slug in lesson_slugs:
                raise CurriculumError(f"{m_where}: duplicate lesson slug '{lesson.slug}'")
            lesson_slugs.add(lesson.slug)
            lessons.append(lesson)

        if markdown_dir.is_dir():
            for md_file in sorted(markdown_dir.glob("*.md")):
                if md_file.stem not in lesson_slugs:
                    raise CurriculumError(f"{md_file}: markdown file is not listed in {where}")

        modules.append(
            ModuleData(
                slug=module_slug,
                title=_string(module, "title", m_where, max_len=200),
                summary=_string(module, "summary", m_where, max_len=1000, required=False),
                lessons=tuple(lessons),
            )
        )

    return CourseData(
        slug=slug,
        title=_string(raw, "title", where, max_len=200),
        summary=_string(raw, "summary", where, max_len=1000, required=False),
        kind=kind,
        stage_number=stage_number if kind == "stage" else None,
        modules=tuple(modules),
    )


def load_curriculum(root: Path) -> CurriculumData:
    concepts = _load_concepts(root)
    concept_slugs = {c.slug for c in concepts}
    courses_dir = root / "courses"
    if not courses_dir.is_dir():
        raise CurriculumError(f"{courses_dir}: folder not found")

    courses = [_load_course(d, concept_slugs) for d in sorted(p for p in courses_dir.iterdir() if p.is_dir())]
    if not courses:
        raise CurriculumError(f"{courses_dir}: no course folders found")

    slugs = [c.slug for c in courses]
    if len(set(slugs)) != len(slugs):
        raise CurriculumError("duplicate course slugs across course folders")
    stages = [c.stage_number for c in courses if c.stage_number is not None]
    if len(set(stages)) != len(stages):
        raise CurriculumError("duplicate stage_number across course folders")
    return CurriculumData(concepts=concepts, courses=tuple(courses))
