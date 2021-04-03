from turtle import reset

import pytest
import json
from sqlalchemy.orm import Session

from core_layer.model.review_question_model import ReviewQuestion
from core_layer.model.review_answer_model import ReviewAnswer, AnswerOption
from core_layer.model.review_model import Review
from core_layer.model.item_model import Item
from core_layer.model.user_model import User

from review_service.get_review import get_review
from core_layer.handler import review_handler

from ....tests.helper import event_creator
from core_layer.connection_handler import get_db_session

from uuid import uuid4


@pytest.fixture
def item_id():
    return str(uuid4())


@pytest.fixture
def review_id():
    return str(uuid4())


@pytest.fixture
def review_question_id():
    return str(uuid4())


@pytest.fixture
def user_id():
    return str(uuid4())


@pytest.fixture
def session(item_id, review_id, review_question_id, user_id):
    session = get_db_session(True, None)

    item = Item()
    item.id = item_id

    user = User()
    user.id = user_id

    review = Review()
    review.id = review_id
    review.item_id = item.id
    review.user_id = user.id

    review_question = ReviewQuestion()
    review_question.id = review_question_id
    review_question.content = "Question content"
    review_question.info = "Question info"
    review_question.hint = "Question hint"

    o1 = AnswerOption(id="1", text="Option 1", value=0)
    o2 = AnswerOption(id="2", text="Option 2", value=1, tooltip="Tooltip 2")
    o3 = AnswerOption(id="3", text="Option 3", value=2)
    o4 = AnswerOption(id="4", text="Option 4", value=3)

    o1.questions = [review_question]
    o2.questions = [review_question]
    o4.questions = [review_question]
    o3.questions = [review_question]

    ## all answers use the same review questions in order to keep the test data small
    reviewanswer1 = generate_review_answer(1, review_id, review_question_id)
    reviewanswer2 = generate_review_answer(0, review_id, review_question_id)
    reviewanswer3 = generate_review_answer(1, review_id, review_question_id)
    reviewanswer4 = generate_review_answer(3, review_id, review_question_id)
    reviewanswer5 = generate_review_answer(2, review_id, review_question_id)
    reviewanswer6 = generate_review_answer(1, review_id, review_question_id)
    reviewanswer7 = generate_review_answer(2, review_id, review_question_id)
    review.review_answers = [reviewanswer1, reviewanswer2, reviewanswer3, reviewanswer4, reviewanswer5, reviewanswer6, reviewanswer7]

    session.add(item)
    session.add(user)
    session.add(review_question)
    ## refernenced ReviewAnswers are stored as well
    session.add(review)

    session.commit()

    return session


def test_get_review(session, user_id, review_id):
    """
    Gets a simple Review
    """

    event = event_creator.get_get_review_event(user_id, review_id)

    resp = get_review(event, None, True, session)

    status = resp["statusCode"]
    assert status == 200

    body = json.loads(resp["body"])
    assert body["id"] == review_id

    assert len(body["questions"]) == 7
    assert body["questions"][0]["id"] != None
    assert body["questions"][0]["content"] != None
    assert body["questions"][0]["info"] != None
    assert body["questions"][0]["hint"] != None
    assert body["questions"][0]["selected_option_id"] == 1
    assert len(body["questions"][0]["options"]) == 4
    assert body["questions"][0]["options"][0]["text"] != None
    assert body["questions"][0]["options"][0]["value"] == 0
    assert body["questions"][0]["options"][1]["tooltip"] != None


def generate_review_answer(answer, review_id, review_question_id):
    return ReviewAnswer(id=str(uuid4()), review_id=review_id, review_question_id=review_question_id, answer=answer, comment='Test Review Answer')
