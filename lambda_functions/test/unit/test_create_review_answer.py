
import json
import pytest

from crud import operations
from crud.model import ReviewQuestion, ReviewAnswer, ReviewPair, Review, Item
from review_answer_handler import create_review_answer
from . import event_creator
from uuid import uuid4


@pytest.fixture
def item_id():
    return str(uuid4())

@pytest.fixture
def junior_review_id():
    return str(uuid4())

@pytest.fixture
def senior_review_id():
    return str(uuid4())

@pytest.fixture
def review_pair_id():
    return str(uuid4())

@pytest.fixture
def review_question_id():
    return str(uuid4())

@pytest.fixture
def session(item_id, junior_review_id, senior_review_id, review_pair_id, review_question_id): 
    session = operations.get_db_session(True, None)

    item = Item()
    item.id = item_id

    junior_review = Review()
    junior_review.id = junior_review_id

    senior_review = Review()
    senior_review.id = senior_review_id

    review_pair = ReviewPair()
    review_pair.id = review_pair_id
    review_pair.item_id = item.id
    review_pair.junior_review_id = junior_review.id
    review_pair.senior_review_id = senior_review.id
    
    review_question = ReviewQuestion()
    review_question.id = review_question_id

    senior_answer = ReviewAnswer()
    senior_answer.id = str(uuid4())
    senior_answer.review_id = senior_review_id
    senior_answer.review_question_id = review_question_id
    senior_answer.answer = 1
    
    session.add(item)
    session.add(junior_review)
    session.add(senior_review)
    session.add(review_pair)
    session.add(review_question)
    session.add(senior_answer)
    session.commit()

    return session

def test_create_review_answer(session, junior_review_id, review_question_id):
    """
    Creates a simple ReviewAnswer without any further steps necessarry
    """

    review_answer = generate_review_answer(2, junior_review_id, review_question_id)

    event = event_creator.get_create_review_answer_event(review_answer)

    resp = create_review_answer(event, None, True, session)
    
    status = resp["statusCode"]
    body = json.loads(resp["body"])

    assert 200 == status
    assert body["id"] != review_answer.id
    assert body["review_id"] == review_answer.review_id
    assert body["review_question_id"] == review_answer.review_question_id
    assert body["answer"] == review_answer.answer
    assert body["comment"] == review_answer.comment

def test_create_multiple_review_answers(session, junior_review_id, review_question_id):
    """
    Creates seven ReviewAnswers and checks if review is closed
    """

    for x in range(7):
        review_answer = generate_review_answer(2, junior_review_id, review_question_id)

        event = event_creator.get_create_review_answer_event(review_answer)

        resp = create_review_answer(event, None, True, session)
        
        status = resp["statusCode"]
        body = json.loads(resp["body"])

        assert 200 == status
        assert body["id"] != review_answer.id
        assert body["review_id"] == review_answer.review_id
        assert body["review_question_id"] == review_answer.review_question_id
        assert body["answer"] == review_answer.answer
        assert body["comment"] == review_answer.comment
    
    item = operations.get_review_by_id(junior_review_id, True, session)

    assert item.status == "closed"

def test_create_review_answer_with_0_answer(session, junior_review_id, senior_review_id, review_question_id):

    review_answer = generate_review_answer(2, junior_review_id, review_question_id)

    event = event_creator.get_create_review_answer_event(review_answer)

    resp = create_review_answer(event, None, True, session)
    
    status = resp["statusCode"]
    body = json.loads(resp["body"])

    assert 200 == status
    assert body["id"] != review_answer.id
    assert body["review_id"] == review_answer.review_id
    assert body["review_question_id"] == review_answer.review_question_id
    assert body["answer"] == review_answer.answer
    assert body["comment"] == review_answer.comment
    
    bad_review_answer = generate_review_answer(0, senior_review_id, review_question_id)    

    bad_event = event_creator.get_create_review_answer_event(bad_review_answer)

    bad_resp = create_review_answer(bad_event, None, True, session)

    review = operations.get_review_by_id(junior_review_id, True, session)
    pair = operations.get_review_pair(review, True, session)

    assert pair.is_good == False


def generate_review_answer(answer, review_id, review_question_id):    
    review_answer = ReviewAnswer()    
    review_answer.id = str(uuid4())
    review_answer.review_id = review_id
    review_answer.review_question_id = review_question_id
    review_answer.answer = answer
    review_answer.comment = 'Test Review Answer'

    return review_answer