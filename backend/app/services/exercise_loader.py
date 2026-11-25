"""Reads exercises and curated resources from curriculum/. Touches no database."""
import json
import re
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

EXERCISE_KINDS = ("code", "quiz", "puzzle")
RESOURCE_KINDS = ("youtube", "article", "docs", "course", "repo")
LEVELS = ("beginner", "intermediate", "advanced")
IDENT = re.compile(r"^[a-z0-9][a-z0-9_-]{0,39}$")
MAX_STARTER_CHARS = 5_000


@dataclass(frozen=True)
class ExerciseData:
    course_slug: str
    module_slug: str
    lesson_slug: str
    slug: str
    title: str
    kind: str
    instructions: str
    pass_score: int
    concepts: tuple[str, ...]
    definition: dict[str, Any]


@dataclass(frozen=True)
class ResourceData:
    title: str
    url: str
    kind: str
    concept: str
    level: str
    is_open_source: bool


@dataclass(frozen=True)
class ExerciseBundle:
    exercises: tuple[ExerciseData, ...]
    resources: tuple[ResourceData, ...]


def _ident(obj: dict[str, Any], key: str, where: str) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not IDENT.fullmatch(value):
        raise CurriculumError(f"{where}: '{key}' must match {IDENT.pattern}")
    return value


def _int_in(value: Any, low: int, high: int, where: str, key: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or not low <= value <= high:
        raise CurriculumError(f"{where}: '{key}' must be an integer from {low} to {high}")
    return value


def _optional_concept(item: dict[str, Any], where: str, allowed: set[str]) -> str | None:
    concept = item.get("concept")
    if concept is None:
        return None
    if concept not in allowed:
        raise CurriculumError(f"{where}: concept '{concept}' is not one of this exercise's concepts")
    return concept


def _quiz(item: dict[str, Any], where: str, allowed: set[str]) -> dict[str, Any]:
    raw = item.get("questions")
    if not isinstance(raw, list) or not 1 <= len(raw) <= 20:
        raise CurriculumError(f"{where}: 'questions' must be a list of 1 to 20 questions")
    seen: set[str] = set()
    questions: list[dict[str, Any]] = []
    for index, entry in enumerate(raw):
        w = f"{where} questions[{index}]"
        question = _object(entry, w)
        qid = _ident(question, "id", w)
        if qid in seen:
            raise CurriculumError(f"{w}: duplicate question id '{qid}'")
        seen.add(qid)
        options = list(_string_list(question, "options", w, max_items=6, max_len=200))
        if len(options) < 2 or len(set(options)) != len(options):
            raise CurriculumError(f"{w}: 'options' needs 2 to 6 different options")
        questions.append(
            {
                "id": qid,
                "prompt": _string(question, "prompt", w, max_len=500),
                "options": options,
                "answer": _int_in(question.get("answer"), 0, len(options) - 1, w, "answer"),
                "explanation": _string(question, "explanation", w, max_len=500),
                "concept": _optional_concept(question, w, allowed),
            }
        )
    return {"questions": questions}


def _code(item: dict[str, Any], where: str, allowed: set[str]) -> dict[str, Any]:
    starter = item.get("starter_code", "")
    if not isinstance(starter, str) or len(starter) > MAX_STARTER_CHARS:
        raise CurriculumError(f"{where}: 'starter_code' must be text under {MAX_STARTER_CHARS} characters")
    timeout = _int_in(item.get("timeout_seconds", 5), 1, 10, where, "timeout_seconds")
    raw = item.get("tests")
    if not isinstance(raw, list) or not 1 <= len(raw) <= 20:
        raise CurriculumError(f"{where}: 'tests' must be a list of 1 to 20 tests")
    seen: set[str] = set()
    tests: list[dict[str, Any]] = []
    for index, entry in enumerate(raw):
        w = f"{where} tests[{index}]"
        test = _object(entry, w)
        tid = _ident(test, "id", w)
        if tid in seen:
            raise CurriculumError(f"{w}: duplicate test id '{tid}'")
        seen.add(tid)
        kind = test.get("type")
        built: dict[str, Any] = {"id": tid, "description": _string(test, "description", w, max_len=200), "type": kind}
        if kind == "return":
            built["call"] = _string(test, "call", w, max_len=200)
            if "expected" not in test:
                raise CurriculumError(f"{w}: 'expected' is required for return tests")
            try:
                json.dumps(test["expected"])
            except (TypeError, ValueError):
                raise CurriculumError(f"{w}: 'expected' must be JSON") from None
            built["expected"] = test["expected"]
        elif kind == "stdout":
            expected = test.get("expected_stdout")
            if not isinstance(expected, str):
                raise CurriculumError(f"{w}: 'expected_stdout' must be a string")
            built["expected_stdout"] = expected
        else:
            raise CurriculumError(f"{w}: 'type' must be 'return' or 'stdout'")
        concept = _optional_concept(test, w, allowed)
        if concept:
            built["concept"] = concept
        tests.append(built)
    return {"starter_code": starter, "timeout_seconds": timeout, "tests": tests}


def _puzzle(item: dict[str, Any], where: str) -> dict[str, Any]:
    if item.get("puzzle_type") != "order":
        raise CurriculumError(f"{where}: 'puzzle_type' must be 'order'")
    lines = item.get("lines")
    if not isinstance(lines, list) or not 2 <= len(lines) <= 12:
        raise CurriculumError(f"{where}: 'lines' must be a list of 2 to 12 lines")
    cleaned: list[str] = []
    for line in lines:
        if not isinstance(line, str) or not line.strip() or len(line) > 120:
            raise CurriculumError(f"{where}: every line must be non-blank text under 120 characters")
        cleaned.append(line.rstrip())
    if len(set(cleaned)) != len(cleaned):
        raise CurriculumError(f"{where}: lines must all be different")
    return {"puzzle_type": "order", "lines": cleaned}


def _load_exercise_file(path: Path, root: Path, curriculum: CurriculumData, lessons: dict, concept_slugs: set[str]):
    where = str(path.relative_to(root))
    course_slug, module_slug, lesson_slug = path.parent.parent.name, path.parent.name, path.stem
    lesson = lessons.get((course_slug, module_slug, lesson_slug))
    if lesson is None:
        raise CurriculumError(f"{where}: no lesson '{lesson_slug}' in {course_slug}/{module_slug}")
    if lesson.content_md is None:
        raise CurriculumError(f"{where}: the lesson is planned; write its Markdown before adding exercises")

    raw = _read_json(path)
    if not isinstance(raw, list) or not 1 <= len(raw) <= 12:
        raise CurriculumError(f"{where}: expected a list of 1 to 12 exercises")
    seen: set[str] = set()
    items: list[ExerciseData] = []
    for index, entry in enumerate(raw):
        w = f"{where}[{index}]"
        item = _object(entry, w)
        slug = _ident(item, "slug", w)
        if slug in seen:
            raise CurriculumError(f"{w}: duplicate exercise slug '{slug}'")
        seen.add(slug)
        kind = item.get("kind")
        if kind not in EXERCISE_KINDS:
            raise CurriculumError(f"{w}: 'kind' must be one of {', '.join(EXERCISE_KINDS)}")
        concepts = _string_list(item, "concepts", w, max_items=8, max_len=80)
        if not concepts:
            raise CurriculumError(f"{w}: at least one concept is required")
        for concept in concepts:
            if concept not in concept_slugs:
                raise CurriculumError(f"{w}: unknown concept '{concept}'")
        allowed = set(concepts)
        if kind == "quiz":
            definition = _quiz(item, w, allowed)
        elif kind == "code":
            definition = _code(item, w, allowed)
        else:
            definition = _puzzle(item, w)
        items.append(
            ExerciseData(
                course_slug=course_slug,
                module_slug=module_slug,
                lesson_slug=lesson_slug,
                slug=slug,
                title=_string(item, "title", w, max_len=200),
                kind=kind,
                instructions=_string(item, "instructions", w, max_len=5000),
                pass_score=_int_in(item.get("pass_score", 70), 1, 100, w, "pass_score"),
                concepts=concepts,
                definition=definition,
            )
        )
    return items


def _load_resources(root: Path, concept_slugs: set[str]) -> tuple[ResourceData, ...]:
    path = root / "resources.json"
    if not path.is_file():
        return ()
    raw = _read_json(path)
    if not isinstance(raw, list):
        raise CurriculumError(f"{path}: expected a list")
    seen: set[str] = set()
    resources: list[ResourceData] = []
    for index, entry in enumerate(raw):
        w = f"resources.json[{index}]"
        item = _object(entry, w)
        url = _string(item, "url", w, max_len=500)
        if not url.startswith("https://"):
            raise CurriculumError(f"{w}: url must start with https://")
        if url in seen:
            raise CurriculumError(f"{w}: duplicate url")
        seen.add(url)
        kind = item.get("kind")
        level = item.get("level")
        concept = item.get("concept")
        if kind not in RESOURCE_KINDS:
            raise CurriculumError(f"{w}: 'kind' must be one of {', '.join(RESOURCE_KINDS)}")
        if level not in LEVELS:
            raise CurriculumError(f"{w}: 'level' must be one of {', '.join(LEVELS)}")
        if concept not in concept_slugs:
            raise CurriculumError(f"{w}: unknown concept '{concept}'")
        is_open = item.get("is_open_source", False)
        if not isinstance(is_open, bool):
            raise CurriculumError(f"{w}: 'is_open_source' must be true or false")
        resources.append(
            ResourceData(
                title=_string(item, "title", w, max_len=200),
                url=url,
                kind=kind,
                concept=concept,
                level=level,
                is_open_source=is_open,
            )
        )
    return tuple(resources)


def load_exercises(root: Path, curriculum: CurriculumData) -> ExerciseBundle:
    concept_slugs = {c.slug for c in curriculum.concepts}
    lessons = {
        (course.slug, module.slug, lesson.slug): lesson
        for course in curriculum.courses
        for module in course.modules
        for lesson in module.lessons
    }
    exercises: list[ExerciseData] = []
    base = root / "exercises"
    if base.is_dir():
        for path in sorted(base.glob("*/*/*.json")):
            exercises.extend(_load_exercise_file(path, root, curriculum, lessons, concept_slugs))
    return ExerciseBundle(exercises=tuple(exercises), resources=_load_resources(root, concept_slugs))
