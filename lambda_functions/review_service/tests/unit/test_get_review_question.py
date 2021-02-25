import pytest
import json
from sqlalchemy.orm import Session
from uuid import uuid4

from core_layer.model.review_question_model import ReviewQuestion
from core_layer.model.review_model import Review
from core_layer.model.review_answer_model import ReviewAnswer
from core_layer.model.review_pair_model import ReviewPair
from core_layer.model.item_model import Item
from core_layer.model.item_type_model import ItemType
from review_service.get_review_question import get_review_question
from review_service.create_review_answer import create_review_answer
from ....tests.helper import event_creator
from core_layer.connection_handler import get_db_session


@pytest.fixture
def item_type():
    item_type = ItemType()
    item_type.id = str(uuid4())
    return item_type


@pytest.fixture
def item(item_type):
    item = Item()
    item.id = str(uuid4())
    item.item_type = item_type
    return item


@pytest.fixture
def review(item):
    review = Review()
    review.id = str(uuid4())
    review.item = item
    return review


@pytest.fixture
def review_pair(review):
    pair = ReviewPair()
    pair.id = str(uuid4())
    pair.junior_review_id = review.id
    return pair


@pytest.fixture
def parent_question_1(item_type):
    question = ReviewQuestion()
    question.id = str(uuid4())
    question.max_children = 1
    question.item_type = item_type
    return question


@pytest.fixture
def child_question_1(parent_question_1, item_type):
    question = ReviewQuestion()
    question.id = str(uuid4())
    question.parent_question = parent_question_1
    question.item_type = item_type
    question.lower_bound = 1
    question.upper_bound = 4
    return question


@pytest.fixture
def event(review):
    return {
        'queryStringParameters': {
            'review_id': review.id
        }
    }


@pytest.fixture
def session(parent_question_1, child_question_1, review, review_pair, item, item_type):
    session = get_db_session(True, None)

    session.add(parent_question_1)
    session.add(child_question_1)
    session.add(review)
    session.add(review_pair)
    session.add(item)
    session.add(item_type)
    session.commit()
    return session


def generate_review_answer(review, review_question):
    review_answer = ReviewAnswer()
    review_answer.id = str(uuid4())
    review_answer.review_id = review.id
    review_answer.review_question_id = review_question.id
    review_answer.answer = 1
    return review_answer


def test_get_review_question(session, parent_question_1, child_question_1, review, event):
    response = get_review_question(event, None, True, session)

    assert response['statusCode'] == 200
    assert json.loads(response['body'])['id'] == parent_question_1.id

    review_answer = generate_review_answer(review, parent_question_1)
    review_answer_event = event_creator.get_create_review_answer_event(
        review_answer)
    resp = create_review_answer(review_answer_event, None, True, session)
    assert resp["statusCode"] == 201
    session.refresh(review)

    response = get_review_question(event, None, True, session)
    assert response['statusCode'] == 200
    assert json.loads(response['body'])['id'] == child_question_1.id
