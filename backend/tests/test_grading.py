import pytest

from app.services import grading

QUIZ = {
    "questions": [
        {"id": "q1", "prompt": "p", "options": ["a", "b"], "answer": 1, "explanation": "e1", "concept": "x"},
        {"id": "q2", "prompt": "p", "options": ["a", "b", "c"], "answer": 2, "explanation": "e2", "concept": None},
    ]
}
CODE = {
    "tests": [
        {"id": "t1", "description": "one", "type": "return", "call": "f()", "expected": 1, "concept": "x"},
        {"id": "t2", "description": "two", "type": "stdout", "expected_stdout": "hi"},
    ]
}
PUZZLE = {"lines": ["a", "b", "c", "d"]}


def test_quiz_scores_and_tallies_concepts():
    result = grading.grade_quiz(QUIZ, ["x", "y"], {"answers": {"q1": 1, "q2": 0}})
    assert result.score == 50
    assert result.concept_stats == {"x": [1, 2], "y": [0, 1]}
    assert [f.correct for f in result.feedback] == [True, False]
    assert result.feedback[1].correct_index == 2


@pytest.mark.parametrize(
    "answer",
    [{}, {"answers": {"q1": 1}}, {"answers": {"q1": 1, "q2": 5}}, {"answers": {"q1": True, "q2": 0}}, {"answers": {"q1": "1", "q2": 0}}],
)
def test_quiz_rejects_malformed_answers(answer):
    with pytest.raises(grading.InvalidAnswer):
        grading.grade_quiz(QUIZ, ["x"], answer)


def test_code_scores_from_reported_results():
    answer = {"code": "x = 1", "results": [{"id": "t1", "passed": True}, {"id": "t2", "passed": False}]}
    result = grading.grade_code(CODE, ["x", "y"], answer)
    assert result.score == 50
    assert result.concept_stats == {"x": [1, 2], "y": [0, 1]}


@pytest.mark.parametrize(
    "answer",
    [
        {"code": "", "results": []},
        {"code": "x", "results": [{"id": "t1", "passed": True}]},
        {"code": "x", "results": [{"id": "t1", "passed": True}, {"id": "t1", "passed": True}]},
        {"code": "x", "results": [{"id": "t1", "passed": True}, {"id": "zz", "passed": True}]},
        {"code": "x", "results": [{"id": "t1", "passed": "yes"}, {"id": "t2", "passed": True}]},
        {"code": "x" * (grading.MAX_CODE_CHARS + 1), "results": []},
    ],
)
def test_code_rejects_malformed_answers(answer):
    with pytest.raises(grading.InvalidAnswer):
        grading.grade_code(CODE, ["x"], answer)


def test_puzzle_counts_items_in_the_right_place():
    assert grading.grade_puzzle(PUZZLE, ["x"], {"order": ["i0", "i1", "i2", "i3"]}).score == 100
    assert grading.grade_puzzle(PUZZLE, ["x"], {"order": ["i1", "i0", "i2", "i3"]}).score == 50


@pytest.mark.parametrize("order", [["i0", "i1"], ["i0", "i0", "i1", "i2"], ["i0", "i1", "i2", "zz"], "i0i1i2i3", None])
def test_puzzle_rejects_non_permutations(order):
    with pytest.raises(grading.InvalidAnswer):
        grading.grade_puzzle(PUZZLE, ["x"], {"order": order})


def test_unknown_kind_is_rejected():
    with pytest.raises(grading.InvalidAnswer):
        grading.grade("essay", {}, [], {})
