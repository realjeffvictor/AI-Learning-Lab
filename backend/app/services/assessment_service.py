import random
import uuid
from collections import defaultdict
from typing import Any

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models import Concept, Exercise, Submission, SubmissionConceptResult
from app.repositories import curriculum_repository, exercise_repository
from app.schemas.assessment import (
    ConceptResult,
    ExercisePublic,
    MasteryRead,
    Recommendation,
    SubmissionResult,
    SubmissionSummary,
)
from app.schemas.curriculum import ConceptRead
from app.services import grading

MAX_LESSON_RECOMMENDATIONS = 4
MAX_RESOURCE_RECOMMENDATIONS = 4
PER_CONCEPT = 2


def shuffled_items(exercise_id: uuid.UUID, lines: list[str]) -> list[dict[str, str]]:
    """Deterministic per exercise, and never already solved."""
    items = [{"id": f"i{index}", "text": text} for index, text in enumerate(lines)]
    shuffled = items[:]
    random.Random(str(exercise_id)).shuffle(shuffled)
    if [i["id"] for i in shuffled] == [i["id"] for i in items]:
        shuffled = shuffled[1:] + shuffled[:1]
    return shuffled


def public_definition(exercise: Exercise) -> dict[str, Any]:
    """The client-visible part of a definition. Quiz answers, explanations and puzzle order never leave the server."""
    definition = exercise.definition
    if exercise.kind == "quiz":
        return {
            "questions": [
                {"id": q["id"], "prompt": q["prompt"], "options": q["options"]} for q in definition["questions"]
            ]
        }
    if exercise.kind == "code":
        return {
            "starter_code": definition["starter_code"],
            "timeout_seconds": definition["timeout_seconds"],
            "tests": [{k: v for k, v in test.items() if k != "concept"} for test in definition["tests"]],
        }
    return {"puzzle_type": "order", "items": shuffled_items(exercise.id, definition["lines"])}


def _concept_reads(concepts: list[Concept]) -> list[ConceptRead]:
    return [ConceptRead(slug=c.slug, name=c.name, category=c.category) for c in concepts]


def list_for_lesson(session: Session, user_id: uuid.UUID, lesson_id: uuid.UUID) -> list[ExercisePublic]:
    if curriculum_repository.get_lesson_by_id(session, lesson_id) is None:
        raise AppError(404, "lesson_not_found", "Lesson not found.")
    exercises = exercise_repository.list_for_lesson(session, lesson_id)
    if not exercises:
        return []
    ids = [exercise.id for exercise in exercises]
    concepts = exercise_repository.concepts_for_many(session, ids)
    stats = exercise_repository.attempt_stats(session, user_id, ids)
    result: list[ExercisePublic] = []
    for exercise in exercises:
        attempts, best, passed = stats.get(exercise.id, (0, None, False))
        result.append(
            ExercisePublic(
                id=exercise.id,
                slug=exercise.slug,
                title=exercise.title,
                kind=exercise.kind,
                position=exercise.position,
                instructions_md=exercise.instructions_md,
                pass_score=exercise.pass_score,
                concepts=_concept_reads(concepts.get(exercise.id, [])),
                definition=public_definition(exercise),
                attempts=attempts,
                best_score=best,
                passed=passed,
            )
        )
    return result


def _recommend(session: Session, stats: dict[str, list[int]], by_slug: dict[str, Concept]) -> list[Recommendation]:
    """Rule-based: weakest concepts first, then published lessons and curated resources tagged with them."""
    weak = sorted(
        (correct / total, slug) for slug, (correct, total) in stats.items() if total and correct < total and slug in by_slug
    )
    slugs = [slug for _, slug in weak][:3]
    if not slugs:
        return []
    ids = [by_slug[slug].id for slug in slugs]

    lessons_by_concept = defaultdict(list)
    for row in exercise_repository.lessons_for_concepts(session, ids):
        lessons_by_concept[row[0]].append(row)
    resources_by_concept = defaultdict(list)
    for resource in exercise_repository.resources_for_concepts(session, ids):
        resources_by_concept[resource.concept_id].append(resource)

    recommendations: list[Recommendation] = []
    lesson_count = resource_count = 0
    for slug in slugs:
        concept = by_slug[slug]
        for _, course_slug, module_slug, lesson_slug, title in lessons_by_concept[concept.id][:PER_CONCEPT]:
            if lesson_count >= MAX_LESSON_RECOMMENDATIONS:
                break
            lesson_count += 1
            recommendations.append(
                Recommendation(
                    type="lesson",
                    concept_slug=concept.slug,
                    concept_name=concept.name,
                    title=title,
                    course_slug=course_slug,
                    module_slug=module_slug,
                    lesson_slug=lesson_slug,
                )
            )
        for resource in resources_by_concept[concept.id][:PER_CONCEPT]:
            if resource_count >= MAX_RESOURCE_RECOMMENDATIONS:
                break
            resource_count += 1
            recommendations.append(
                Recommendation(
                    type="resource",
                    concept_slug=concept.slug,
                    concept_name=concept.name,
                    title=resource.title,
                    url=resource.url,
                    resource_kind=resource.kind,
                    is_open_source=resource.is_open_source,
                )
            )
    return recommendations


def submit(session: Session, user_id: uuid.UUID, exercise_id: uuid.UUID, answer: dict[str, Any]) -> SubmissionResult:
    exercise = exercise_repository.get(session, exercise_id)
    if exercise is None:
        raise AppError(404, "exercise_not_found", "Exercise not found.")
    concepts = exercise_repository.concepts_for(session, exercise.id)
    by_slug = {concept.slug: concept for concept in concepts}

    try:
        graded = grading.grade(exercise.kind, exercise.definition, list(by_slug), answer)
    except grading.InvalidAnswer as exc:
        raise AppError(422, "invalid_answer", str(exc)) from None

    passed = graded.score >= exercise.pass_score
    submission = exercise_repository.add_submission(
        session,
        Submission(user_id=user_id, exercise_id=exercise.id, answer=answer, score=graded.score, passed=passed),
    )
    session.add_all(
        SubmissionConceptResult(
            submission_id=submission.id, concept_id=by_slug[slug].id, correct=correct, total=total
        )
        for slug, (correct, total) in graded.concept_stats.items()
        if slug in by_slug and total > 0
    )
    session.commit()

    return SubmissionResult(
        id=submission.id,
        score=graded.score,
        passed=passed,
        pass_score=exercise.pass_score,
        attempt_number=exercise_repository.count_attempts(session, user_id, exercise.id),
        feedback=graded.feedback,
        concept_results=[
            ConceptResult(slug=slug, name=by_slug[slug].name, correct=correct, total=total)
            for slug, (correct, total) in graded.concept_stats.items()
            if slug in by_slug
        ],
        recommendations=_recommend(session, graded.concept_stats, by_slug),
        created_at=submission.created_at,
    )


def history(session: Session, user_id: uuid.UUID, exercise_id: uuid.UUID) -> list[SubmissionSummary]:
    if exercise_repository.get(session, exercise_id) is None:
        raise AppError(404, "exercise_not_found", "Exercise not found.")
    return [
        SubmissionSummary.model_validate(row) for row in exercise_repository.list_submissions(session, user_id, exercise_id)
    ]


def mastery(session: Session, user_id: uuid.UUID) -> list[MasteryRead]:
    return [
        MasteryRead(slug=slug, name=name, category=category, correct=int(correct), total=int(total))
        for slug, name, category, correct, total in exercise_repository.mastery(session, user_id)
    ]
