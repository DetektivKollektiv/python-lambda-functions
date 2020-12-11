
import json
import pytest
from sqlalchemy.orm import Session

from core_layer.connection_handler import get_db_session

from core_layer.model.review_question_model import ReviewQuestion
from core_layer.model.review_answer_model import ReviewAnswer
from core_layer.model.review_pair_model import ReviewPair
from core_layer.model.review_model import Review
from core_layer.model.item_model import Item
from core_layer.model.user_model import User

from review_service.create_review_answer import create_review_answer
from core_layer.handler import review_handler

from ....tests.helper import event_creator

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
def user_id():
    return str(uuid4())


@pytest.fixture
def session(item_id, junior_review_id, senior_review_id, review_pair_id, review_question_id, user_id):
    session = get_db_session(True, None)

    item = Item()
    item.id = item_id

    user = User()
    user.id = user_id
    user.experience_points = 0

    junior_review = Review()
    junior_review.id = junior_review_id
    junior_review.item_id = item.id
    junior_review.user_id = user.id

    senior_review = Review()
    senior_review.id = senior_review_id
    senior_review.item_id = item.id

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
    session.add(user)
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

    review_answer = generate_review_answer(
        2, junior_review_id, review_question_id)

    event = event_creator.get_create_review_answer_event(review_answer)

    resp = create_review_answer(event, None, True, session)

    status = resp["statusCode"]
    body = json.loads(resp["body"])

    assert 201 == status
    assert body["id"] != review_answer.id
    assert body["review_id"] == review_answer.review_id
    assert body["review_question_id"] == review_answer.review_question_id
    assert body["answer"] == review_answer.answer
    assert body["comment"] == review_answer.comment


def test_create_multiple_review_answers(session, junior_review_id, review_question_id):
    # TODO:
    """
    Creates seven ReviewAnswers and checks if review is closed
    """

    for _ in range(7):
        review_answer = generate_review_answer(
            2, junior_review_id, review_question_id)

        event = event_creator.get_create_review_answer_event(review_answer)

        resp = create_review_answer(event, None, True, session)

        status = resp["statusCode"]
        body = json.loads(resp["body"])

        assert 201 == status
        assert body["id"] != review_answer.id
        assert body["review_id"] == review_answer.review_id
        assert body["review_question_id"] == review_answer.review_question_id
        assert body["answer"] == review_answer.answer
        assert body["comment"] == review_answer.comment

    item = review_handler.get_review_by_id(junior_review_id, True, session)

    assert item.status == "closed"


def generate_review_answer(answer, review_id, review_question_id):
    review_answer = ReviewAnswer()
    review_answer.id = str(uuid4())
    review_answer.review_id = review_id
    review_answer.review_question_id = review_question_id
    review_answer.answer = answer
    review_answer.comment = 'Test Review Answer'

    return review_answer
