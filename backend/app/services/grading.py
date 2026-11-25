"""Pure grading functions: no database, no HTTP. Each returns a score plus per-item feedback and per-concept tallies.

Code exercises are graded from test results reported by the browser (the server cannot run student code),
so a code score is self-reported. Quizzes and puzzles are graded entirely here."""
from dataclasses import dataclass, field
from typing import Any

from app.schemas.assessment import FeedbackItem

MAX_CODE_CHARS = 20_000


class InvalidAnswer(Exception):
    """The submitted answer does not have the shape the exercise expects."""


@dataclass
class GradeResult:
    score: int
    feedback: list[FeedbackItem]
    concept_stats: dict[str, list[int]] = field(default_factory=dict)  # slug -> [correct, total]


def _tally(stats: dict[str, list[int]], slugs: list[str], correct: bool) -> None:
    for slug in slugs:
        entry = stats.setdefault(slug, [0, 0])
        entry[1] += 1
        entry[0] += int(correct)


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def grade_quiz(definition: dict[str, Any], exercise_concepts: list[str], answer: dict[str, Any]) -> GradeResult:
    given = answer.get("answers")
    questions = definition["questions"]
    if not isinstance(given, dict) or set(given) != {q["id"] for q in questions}:
        raise InvalidAnswer("Answer every question.")

    stats: dict[str, list[int]] = {}
    feedback: list[FeedbackItem] = []
    right = 0
    for question in questions:
        value = given[question["id"]]
        if not _is_int(value) or not 0 <= value < len(question["options"]):
            raise InvalidAnswer("Each answer must be the number of one of the options.")
        correct = value == question["answer"]
        right += int(correct)
        _tally(stats, [question["concept"]] if question.get("concept") else exercise_concepts, correct)
        feedback.append(
            FeedbackItem(
                id=question["id"], correct=correct, message=question["explanation"], correct_index=question["answer"]
            )
        )
    return GradeResult(round(100 * right / len(questions)), feedback, stats)


def grade_code(definition: dict[str, Any], exercise_concepts: list[str], answer: dict[str, Any]) -> GradeResult:
    code = answer.get("code")
    results = answer.get("results")
    if not isinstance(code, str) or not code.strip():
        raise InvalidAnswer("Submit your code.")
    if len(code) > MAX_CODE_CHARS:
        raise InvalidAnswer(f"Code is longer than {MAX_CODE_CHARS} characters.")
    if not isinstance(results, list):
        raise InvalidAnswer("Submit the test results with your code.")

    by_id: dict[str, bool] = {}
    for item in results:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not isinstance(item.get("passed"), bool):
            raise InvalidAnswer("Each test result needs an id and a passed flag.")
        if item["id"] in by_id:
            raise InvalidAnswer("Duplicate test result.")
        by_id[item["id"]] = item["passed"]

    tests = definition["tests"]
    if set(by_id) != {t["id"] for t in tests}:
        raise InvalidAnswer("Test results do not match this exercise.")

    stats: dict[str, list[int]] = {}
    feedback: list[FeedbackItem] = []
    for test in tests:
        correct = by_id[test["id"]]
        _tally(stats, [test["concept"]] if test.get("concept") else exercise_concepts, correct)
        feedback.append(FeedbackItem(id=test["id"], correct=correct, message=test["description"]))
    return GradeResult(round(100 * sum(by_id.values()) / len(tests)), feedback, stats)


def puzzle_item_ids(definition: dict[str, Any]) -> list[str]:
    return [f"i{index}" for index in range(len(definition["lines"]))]


def grade_puzzle(definition: dict[str, Any], exercise_concepts: list[str], answer: dict[str, Any]) -> GradeResult:
    expected = puzzle_item_ids(definition)
    order = answer.get("order")
    if not isinstance(order, list) or sorted(order) != sorted(expected) or not all(isinstance(i, str) for i in order):
        raise InvalidAnswer("Use every line exactly once.")

    stats: dict[str, list[int]] = {}
    feedback: list[FeedbackItem] = []
    right = 0
    for position, item_id in enumerate(order):
        correct = item_id == expected[position]
        right += int(correct)
        _tally(stats, exercise_concepts, correct)
        feedback.append(FeedbackItem(id=item_id, correct=correct))
    return GradeResult(round(100 * right / len(expected)), feedback, stats)


def grade(kind: str, definition: dict[str, Any], exercise_concepts: list[str], answer: dict[str, Any]) -> GradeResult:
    if kind == "quiz":
        return grade_quiz(definition, exercise_concepts, answer)
    if kind == "code":
        return grade_code(definition, exercise_concepts, answer)
    if kind == "puzzle":
        return grade_puzzle(definition, exercise_concepts, answer)
    raise InvalidAnswer(f"Unknown exercise kind '{kind}'.")
