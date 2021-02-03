import pytest
from uuid import uuid4
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from core_layer.model import User
from core_layer.handler import user_handler
from core_layer import connection_handler
from core_layer.handler.tests.unit.helper import level_creator, user_creator, review_creator, item_creator


@pytest.fixture
def user_id_1():
    return str(uuid4())


@pytest.fixture
def user_id_2():
    return str(uuid4())


@pytest.fixture
def user_id_3():
    return str(uuid4())


@pytest.fixture
def review_id_1():
    return str(uuid4())


@pytest.fixture
def review_id_2():
    return str(uuid4())


@pytest.fixture
def review_id_3():
    return str(uuid4())


@pytest.fixture
def item_id_1():
    return str(uuid4())


@pytest.fixture
def item_id_2():
    return str(uuid4())


@pytest.fixture
def fixtures(item_id_1, item_id_2, user_id_1, user_id_2, user_id_3, review_id_1, review_id_2, review_id_3):

    item1 = item_creator.create_item(item_id_1)
    item2 = item_creator.create_item(item_id_2)

    level1 = level_creator.create_level(1, 0)
    level2 = level_creator.create_level(2, 5)
    level3 = level_creator.create_level(3, 10)

    user1 = user_creator.create_user(user_id_1, level1, 0)
    user2 = user_creator.create_user(user_id_2, level1, 1)
    user3 = user_creator.create_user(user_id_3, level2, 8)

    review1 = review_creator.create_review(
        review_id_1, item1.id, user_id_1, "closed")
    review2 = review_creator.create_review(
        review_id_2, item2.id, user_id_1, "closed", datetime.now() - timedelta(days=3))
    review3 = review_creator.create_review(
        review_id_3, item1.id, user_id_3, "closed")

    return[item1, item2, level1, level2, level3, user1, user2, user3, review1, review2, review3]


@pytest.fixture
def session(fixtures):
    session = connection_handler.get_db_session(True, None)

    session.add_all(fixtures)
    session.commit()
    return session


def test_get_user_total_rank(session, user_id_1, user_id_2, user_id_3):
    user_1 = session.query(User).filter(User.id == user_id_1).one()
    user_2 = session.query(User).filter(User.id == user_id_2).one()
    user_3 = session.query(User).filter(User.id == user_id_3).one()
    user_rank_1 = user_handler.get_user_rank(user_1, False, True, session)
    user_rank_3 = user_handler.get_user_rank(user_3, False, True, session)
    # with pytest.raises(Exception):
    user_rank_2 = user_handler.get_user_rank(user_2, False, True, session)

    assert user_rank_1 == 1
    assert user_rank_3 == 2
    assert user_rank_2 == 3


def test_get_user_level_rank(session, user_id_1, user_id_2, user_id_3):
    user_1 = session.query(User).filter(User.id == user_id_1).one()
    user_2 = session.query(User).filter(User.id == user_id_2).one()
    user_3 = session.query(User).filter(User.id == user_id_3).one()
    user_rank_1 = user_handler.get_user_rank(user_1, True, True, session)
    user_rank_3 = user_handler.get_user_rank(user_3, True, True, session)
    user_rank_2 = user_handler.get_user_rank(user_2, True, True, session)

    assert user_rank_1 == 1
    assert user_rank_3 == 1
    assert user_rank_2 == 2


def test_get_total_solved_cases(session, user_id_1, user_id_2, user_id_3):
    user_1 = session.query(User).filter(User.id == user_id_1).one()
    user_2 = session.query(User).filter(User.id == user_id_2).one()
    user_3 = session.query(User).filter(User.id == user_id_3).one()
    solved_cases_1 = user_handler.get_solved_cases(
        user_1, False, True, session)
    solved_cases_2 = user_handler.get_solved_cases(
        user_2, False, True, session)
    solved_cases_3 = user_handler.get_solved_cases(
        user_3, False, True, session)

    assert solved_cases_1 == 2
    assert solved_cases_2 == 0
    assert solved_cases_3 == 1


def test_get_today_solved_cases(session, user_id_1, user_id_2, user_id_3):
    user_1 = session.query(User).filter(User.id == user_id_1).one()
    user_2 = session.query(User).filter(User.id == user_id_2).one()
    user_3 = session.query(User).filter(User.id == user_id_3).one()
    solved_cases_1 = user_handler.get_solved_cases(
        user_1, True, True, session)
    solved_cases_2 = user_handler.get_solved_cases(
        user_2, True, True, session)
    solved_cases_3 = user_handler.get_solved_cases(
        user_3, True, True, session)

    assert solved_cases_1 == 1
    assert solved_cases_2 == 0
    assert solved_cases_3 == 1


def test_exp_needed(session, user_id_1, user_id_2, user_id_3):
    user_1 = session.query(User).filter(User.id == user_id_1).one()
    user_2 = session.query(User).filter(User.id == user_id_2).one()
    user_3 = session.query(User).filter(User.id == user_id_3).one()
    exp_needed_1 = user_handler.get_needed_exp(user_1, True, session)
    exp_needed_2 = user_handler.get_needed_exp(user_2, True, session)
    exp_needed_3 = user_handler.get_needed_exp(user_3, True, session)

    assert exp_needed_1 == 5
    assert exp_needed_2 == 4
    assert exp_needed_3 == 2
