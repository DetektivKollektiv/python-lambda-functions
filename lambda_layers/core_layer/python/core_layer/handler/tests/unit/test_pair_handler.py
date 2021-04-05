import pytest
from core_layer.model.review_pair_model import ReviewPair
from core_layer.model.review_model import Review
from core_layer.model.review_answer_model import ReviewAnswer

from helper import review_answer_creator
from core_layer.handler import review_pair_handler

data = [
    (1, 1, 1, 1, 0),
    (1, 1, 2, 2, 1.0),
    (2, 2, 1, 1, 1.0),
    (2, 2, 2, 2, 0),
    (2, 2, 2, 2, 0),
]


@pytest.mark.parametrize("junior_answer_1, junior_answer_2, senior_answer_1, senior_answer_2, expected", data)
def test_simple_pair(junior_answer_1: int, junior_answer_2: int, senior_answer_1: int, senior_answer_2: int, expected: float):
    """
    Tests simple data sets to ensure difference between review answers is correctly computed
    """

    pair = ReviewPair()

    pair.junior_review = Review()
    pair.senior_review = Review()

    pair.junior_review.review_answers = [
        review_answer_creator.generate_answer(junior_answer_1),
        review_answer_creator.generate_answer(junior_answer_2)
    ]

    pair.senior_review.review_answers = [
        review_answer_creator.generate_answer(senior_answer_1),
        review_answer_creator.generate_answer(senior_answer_2)
    ]

    result = review_pair_handler.compute_difference(pair)

    assert result == expected
