import pytest
import crud.operations as operations
from crud.model import ReviewAnswer
import test.unit.helper.review_answer_creator as review_answer_creator

answers = [
    (1,1,1,1,1,1,1,1),
    (2,2,2,2,2,2,2,2),
    (1,2,3,4,5,6,7,4),
    (7,6,5,4,3,2,1,4),
    (1,1,1,1,1,1,4.5,1.5)
]

@pytest.mark.parametrize("a, b, c, d, e, f, g, expected", answers)
def test_simple_compute(a, b, c, d, e, f, g, expected):
    """
    Tests simple data sets to ensure review result is computed correctly.
    """

    review_answers = [
        review_answer_creator.generate_answer(a),
        review_answer_creator.generate_answer(b),
        review_answer_creator.generate_answer(c),
        review_answer_creator.generate_answer(d),
        review_answer_creator.generate_answer(e), 
        review_answer_creator.generate_answer(f),
        review_answer_creator.generate_answer(g)
    ]

    result = operations.compute_review_result(review_answers)

    assert result == expected

def test_error_none():
    """
    Tests if passing None leads to a TypeError.
    """

    with pytest.raises(TypeError):
        review_answers = None
        result = operations.compute_review_result(review_answers)
        
def test_error_no_list():
    """
    Tests if passing another type than a list leads to a TypeError.
    """

    with pytest.raises(TypeError):
        review_answers = 123
        result = operations.compute_review_result(review_answers)
        
def test_error_empty_list():
    """
    Tests if passing an empty list leads to a ValueError.
    """

    with pytest.raises(ValueError):
        review_answers = []
        result = operations.compute_review_result(review_answers)
        
def test_error_list_wrong_value():
    """
    Tests if passing a list with values other then ReviewAnswers leads to a AttributeError.
    """

    with pytest.raises(AttributeError):
        review_answers = [1,2,3]
        result = operations.compute_review_result(review_answers)
        
def test_error_list_value_missing_answer():
    """
    Tests if passing a list with values missing an answer leads to a TypeError.
    """

    with pytest.raises(TypeError):
        review_answers = [
            review_answer_creator.generate_answer(3),
            review_answer_creator.generate_answer(2),
            review_answer_creator.generate_answer(1),
            review_answer_creator.generate_answer(None)
        ]
        result = operations.compute_review_result(review_answers)
    
