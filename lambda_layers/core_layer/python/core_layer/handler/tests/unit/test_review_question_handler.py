
import pytest
from uuid import uuid4
from sqlalchemy.orm.exc import NoResultFound

from core_layer.model import ItemType
from core_layer.handler import review_question_handler
from core_layer import connection_handler
from helper import item_type_creator, review_question_creator


@pytest.fixture
def type_id_1():
    return str(uuid4())


@pytest.fixture
def type_id_2():
    return str(uuid4())


@pytest.fixture
def question_id_1():
    return str(uuid4())


@pytest.fixture
def question_id_2():
    return str(uuid4())


@pytest.fixture
def fixtures(type_id_1, type_id_2, question_id_1, question_id_2):
    type1 = item_type_creator.create_item_type(type_id_1, "type1")
    type2 = item_type_creator.create_item_type(type_id_2, "type2")

    question1 = review_question_creator.create_review_question(
        question_id_1, type_id_1)
    question2 = review_question_creator.create_review_question(
        question_id_2, type_id_2)

    return [type1, type2, question1, question2]


@pytest.fixture
def session(fixtures):
    session = connection_handler.get_db_session(True, None)

    session.add_all(fixtures)
    session.commit()


def test_get_all_questions(session):
    review_questions = review_question_handler.get_all_review_questions_db(
        True, session)

    assert len(review_questions) == 2


def test_get_question_by_id(session, question_id_1, question_id_2):
    review_question_1 = review_question_handler.get_review_question_by_id(
        question_id_1, True, session)
    review_question_2 = review_question_handler.get_review_question_by_id(
        question_id_2, True, session)

    with pytest.raises(NoResultFound):
        review_question_3 = review_question_handler.get_review_question_by_id(
            str(uuid4()), True, session)

    assert review_question_1 != None
    assert review_question_2 != None
    assert review_question_1.id == question_id_1
    assert review_question_2.id == question_id_2


def test_get_question_by_type_id(session, type_id_1, type_id_2, question_id_1, question_id_2):
    review_questions_1 = review_question_handler.get_review_questions_by_item_id(
        type_id_1, True, session)
    review_questions_2 = review_question_handler.get_review_questions_by_item_id(
        type_id_2, True, session)
    review_questions_3 = review_question_handler.get_review_questions_by_item_id(
        str(uuid4()), True, session)

    assert len(review_questions_1) == 1
    assert review_questions_1[0].id == question_id_1

    assert len(review_questions_2) == 1
    assert review_questions_2[0].id == question_id_2

    assert len(review_questions_3) == 0
