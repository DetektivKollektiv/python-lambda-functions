
import pytest
from uuid import uuid4
from sqlalchemy.orm.exc import NoResultFound

from core_layer.model.review_question_model import ReviewQuestion
from core_layer.handler import review_question_handler
from core_layer.db_handler import Session
from core_layer.handler.tests.unit.helper import item_type_creator, review_question_creator, review_creator, item_creator


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
def child_question1(question_id_1, type_id_1) -> ReviewQuestion:
    cq1 = ReviewQuestion()
    cq1.id = str(uuid4())
    cq1.parent_question_id = question_id_1
    cq1.item_type_id = type_id_1
    return cq1


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


def test_get_all_questions(fixtures):

    with Session() as session:

        session.add_all(fixtures)
        session.commit()

        review_questions = review_question_handler.get_all_review_questions_db(session)

        assert len(review_questions) == 3


def test_get_question_by_id(fixtures, question_id_1, question_id_2, question_id_3):
    with Session() as session:

        session.add_all(fixtures)
        session.commit()
        review_question_1 = review_question_handler.get_review_question_by_id(question_id_1, session)
        review_question_2 = review_question_handler.get_review_question_by_id(question_id_2, session)
        review_question_3 = review_question_handler.get_review_question_by_id(question_id_3, session)

        with pytest.raises(NoResultFound):
            review_question_3 = review_question_handler.get_review_question_by_id(str(uuid4()), session)

        assert review_question_1 is not None
        assert review_question_2 is not None
        assert review_question_3 is not None
        assert review_question_1.id == question_id_1
        assert review_question_2.id == question_id_2
        assert review_question_3.id == question_id_3


def test_get_question_by_type_id(fixtures, type_id_1, type_id_2, question_id_1, question_id_2):
    with Session() as session:

        session.add_all(fixtures)
        session.commit()

        review_questions_1 = review_question_handler.get_review_questions_by_item_type_id(type_id_1, session)
        review_questions_2 = review_question_handler.get_review_questions_by_item_type_id(type_id_2, session)
        review_questions_3 = review_question_handler.get_review_questions_by_item_type_id(str(uuid4()), session)

        assert len(review_questions_1) == 1
        assert review_questions_1[0].id == question_id_1

        assert len(review_questions_2) == 2
        assert review_questions_2[0].id == question_id_2

        assert len(review_questions_3) == 0


def test_get_all_parent_questions(fixtures, child_question1, type_id_1):
    with Session() as session:

        session.add_all(fixtures)
        session.add(child_question1)
        session.commit()

        all_questions_type_1 = review_question_handler.get_review_questions_by_item_type_id(type_id_1, session)
        assert len(all_questions_type_1) == 2
        assert child_question1 in all_questions_type_1
        parent_questions_type_1 = review_question_handler.get_all_parent_questions(type_id_1, session)
        assert len(parent_questions_type_1) == 1
        assert child_question1 not in parent_questions_type_1
