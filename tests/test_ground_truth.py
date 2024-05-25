from evaluation.groundtruth import compare_ground_truth, calculate_ground_truth_scores
from schema.data import RawData, RawDataContext
import pytest


@pytest.fixture
def ground_truth_data() -> RawData:
    context = [
        RawDataContext(
            id="1",
            text="John likes to travel to the middle eastern, especially Qatar during the autumn period",
            has_answer=False,
        ),
        RawDataContext(
            id="2",
            text="Johnny likes to spend his free time in the heart of Central Park",
            has_answer=True,
        ),
        RawDataContext(
            id="3",
            text="You can find Johnny spending most of his time, strolling down the Central Park with his dog, almost every Sunday morning",
            has_answer=True,
        ),
    ]
    return RawData(
        data_id=1,
        answer_with_citation="Johnny likes to spend his time at the Central Park [2] with his dog [3].",
        answer="Johnny likes to spend his time at the Central Park with his dog.",
        question="What does Johnny like to do?",
        docs=context,
    )


def test_positive_compare_ground_truth(ground_truth_data: RawData):
    """Test the comparison of ground truth to obtain correctly identified results"""
    generated_answer: str = ground_truth_data.answer_with_citation
    citation_evaluation = compare_ground_truth(generated_answer, ground_truth_data)

    assert [
        text_citation_pair[1]
        for text_citation_pair in citation_evaluation.correct_valid_citations
    ] == [
        "2",
        "3",
    ]
    assert citation_evaluation.unmatched_text == ""
    assert citation_evaluation.wrong_invalid_citations == []
    assert citation_evaluation.wrong_text_citations == []
    assert citation_evaluation.correct_skipped_docs == [
        (ground_truth_data.docs[0].id, ground_truth_data.docs[0].text)
    ]
    assert citation_evaluation.missing_citations == []

    ground_truth_scores = calculate_ground_truth_scores(citation_evaluation)
    assert ground_truth_scores.accuracy_score == 1
    assert ground_truth_scores.precision_score == 1
    assert ground_truth_scores.recall_score == 1
    assert ground_truth_scores.f1_score == 1


def test_full_negative_compare_ground_truth(ground_truth_data: RawData):
    """Test the comparison of ground truth to obtain negatively identified results"""
    generated_answer = (
        "Johnny likes to spend his time at the Central Park [1] with his dog."
    )
    citation_evaluation = compare_ground_truth(generated_answer, ground_truth_data)

    assert citation_evaluation.wrong_invalid_citations == []
    assert citation_evaluation.wrong_text_citations == [
        ("Johnny likes to spend his time at the Central Park ", "1")
    ]
    assert citation_evaluation.correct_valid_citations == []
    assert citation_evaluation.correct_skipped_docs == []
    assert citation_evaluation.missing_citations == [
        ("Johnny likes to spend his time at the Central Park ", "2"),
        (" with his dog ", "3"),
    ]
    assert citation_evaluation.all_citations == {
        "1": ["Johnny likes to spend his time at the Central Park "]
    }
    assert citation_evaluation.unmatched_text == "with his dog"

    ground_truth_scores = calculate_ground_truth_scores(citation_evaluation)
    assert ground_truth_scores.accuracy_score == 0
    assert ground_truth_scores.precision_score == 0
    assert ground_truth_scores.recall_score == 0
    assert ground_truth_scores.f1_score == 0


def test_invalid_citation_compare_ground_truth(ground_truth_data: RawData):
    """Test the comparison of ground truth to obtain negatively identified results"""
    generated_answer = (
        "Johnny likes to spend his time at the Central Park [3] with his dog. [3]"
    )
    citation_evaluation = compare_ground_truth(generated_answer, ground_truth_data)

    assert citation_evaluation.wrong_invalid_citations == []
    assert citation_evaluation.wrong_text_citations == [
        ("Johnny likes to spend his time at the Central Park ", "3")
    ]
    assert citation_evaluation.correct_valid_citations == [(" with his dog. ", "3")]
    assert citation_evaluation.correct_skipped_docs == [
        (ground_truth_data.docs[0].id, ground_truth_data.docs[0].text)
    ]
    assert citation_evaluation.missing_citations == [
        ("Johnny likes to spend his time at the Central Park ", "2"),
    ]
    assert citation_evaluation.all_citations == {
        "3": ["Johnny likes to spend his time at the Central Park ", " with his dog. "]
    }
    assert citation_evaluation.unmatched_text == ""

    ground_truth_scores = calculate_ground_truth_scores(citation_evaluation)
    assert ground_truth_scores.accuracy_score == 0.5
    assert ground_truth_scores.precision_score == 0.5
    assert ground_truth_scores.recall_score == 0.5
    assert ground_truth_scores.f1_score == 0.5
