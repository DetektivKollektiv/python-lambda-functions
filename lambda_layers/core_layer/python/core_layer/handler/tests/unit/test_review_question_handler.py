
import pytest
from uuid import uuid4
from sqlalchemy.orm.exc import NoResultFound

from core_layer.model import ItemType
from core_layer.handler import review_question_handler, review_handler, review_answer_handler
from core_layer import connection_handler
from helper import item_type_creator, review_question_creator, review_creator, item_creator, review_answer_creator


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
def question_id_3():
    return str(uuid4())


@pytest.fixture
def review_id_1():
    return str(uuid4())


@pytest.fixture
def review_id_2():
    return str(uuid4())


@pytest.fixture
def item_id_1():
    return str(uuid4())


@pytest.fixture
def item_id_2():
    return str(uuid4())


@pytest.fixture
def fixtures(type_id_1, type_id_2, question_id_1, question_id_2, question_id_3, item_id_1, item_id_2, review_id_1, review_id_2):
    type1 = item_type_creator.create_item_type(type_id_1, "type1")
    type2 = item_type_creator.create_item_type(type_id_2, "type2")

    question1 = review_question_creator.create_review_question(
        question_id_1, type_id_1)
    question2 = review_question_creator.create_review_question(
        question_id_2, type_id_2)
    question3 = review_question_creator.create_review_question(
        question_id_3, type_id_2)

    item1 = item_creator.create_item(item_id_1, type_id_1)
    item2 = item_creator.create_item(item_id_2, type_id_2)

    review1 = review_creator.create_review(review_id_1, item_id_1)
    review2 = review_creator.create_review(review_id_2, item_id_2)

    return [type1, type2, question1, question2, question3, item1, item2, review1, review2]


@pytest.fixture
def session(fixtures):
    session = connection_handler.get_db_session(True, None)

    session.add_all(fixtures)
    session.commit()

    return session


def test_get_all_questions(session):
    review_questions = review_question_handler.get_all_review_questions_db(
        True, session)

    assert len(review_questions) == 3


def test_get_question_by_id(session, question_id_1, question_id_2, question_id_3):
    review_question_1 = review_question_handler.get_review_question_by_id(
        question_id_1, True, session)
    review_question_2 = review_question_handler.get_review_question_by_id(
        question_id_2, True, session)
    review_question_3 = review_question_handler.get_review_question_by_id(
        question_id_3, True, session)

    with pytest.raises(NoResultFound):
        review_question_3 = review_question_handler.get_review_question_by_id(
            str(uuid4()), True, session)

    assert review_question_1 is not None
    assert review_question_2 is not None
    assert review_question_3 is not None
    assert review_question_1.id == question_id_1
    assert review_question_2.id == question_id_2
    assert review_question_3.id == question_id_3


def test_get_question_by_type_id(session, type_id_1, type_id_2, question_id_1, question_id_2):
    review_questions_1 = review_question_handler.get_review_questions_by_item_id(
        type_id_1, True, session)
    review_questions_2 = review_question_handler.get_review_questions_by_item_id(
        type_id_2, True, session)
    review_questions_3 = review_question_handler.get_review_questions_by_item_id(
        str(uuid4()), True, session)

    assert len(review_questions_1) == 1
    assert review_questions_1[0].id == question_id_1

    assert len(review_questions_2) == 2
    assert review_questions_2[0].id == question_id_2

    assert len(review_questions_3) == 0


def test_get_next_question_no_review():
    with pytest.raises(AttributeError):
        review_question = review_question_handler.get_next_question_db(
            None, None, True, None)


def test_get_next_question_simple(session, review_id_1, review_id_2, question_id_1, question_id_2):
    review1 = review_handler.get_review_by_id(review_id_1, True, session)
    assert review1 is not None

    review2 = review_handler.get_review_by_id(review_id_2, True, session)
    assert review2 is not None

    question1 = review_question_handler.get_next_question_db(
        review1, None, True, session)
    assert question1 is not None
    assert question1.id == question_id_1

    question2 = review_question_handler.get_next_question_db(
        review2, None, True, session)
    assert question2 is not None
    assert question2.id == question_id_2


def test_get_next_question_simple(session, review_id_1, review_id_2, question_id_1, question_id_2, question_id_3):
    review1 = review_handler.get_review_by_id(review_id_1, True, session)
    assert review1 is not None

    review2 = review_handler.get_review_by_id(review_id_2, True, session)
    assert review2 is not None

    question1 = review_question_handler.get_next_question_db(
        review1, None, True, session)
    assert question1 is not None
    assert question1.id == question_id_1

    question2 = review_question_handler.get_next_question_db(
        review2, None, True, session)
    assert question2 is not None
    assert question2.id in [question_id_2, question_id_3]

    review_answer1 = review_answer_creator.generate_answer(
        1, review2.id, question2.id)
    review_answer_handler.create_review_answer(review_answer1, True, session)

    question3 = review_question_handler.get_next_question_db(
        review2, question2, True, session)
    assert question3 is not None
    assert question3.id in [question_id_2,
                            question_id_3] and question3.id != question2.id

    review_answer2 = review_answer_creator.generate_answer(
        1, review2.id, question3.id)
    review_answer_handler.create_review_answer(review_answer2, True, session)

    with pytest.raises(Exception):
        question4 = review_question_handler.get_next_question_db(
            review2, question3, True, session)
