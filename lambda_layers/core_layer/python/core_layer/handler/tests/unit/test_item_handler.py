import pytest
from core_layer.model.item_model import Item
from core_layer.model.user_model import User
from core_layer.handler import item_handler
from helper import review_answer_creator
from core_layer.connection_handler import get_db_session
from uuid import uuid4


@pytest.fixture
def open_item1():
    item = Item()
    item.id = str(uuid4())
    item.status = "open"
    return item


@pytest.fixture
def open_item2():
    item = Item()
    item.id = str(uuid4())
    item.status = "open"
    return item


@pytest.fixture
def closed_item():
    item = Item()
    item.id = str(uuid4())
    item.status = "closed"
    return item


@pytest.fixture
def unconfirmed_item():
    item = Item()
    item.id = str(uuid4())
    item.status = "unconfirmed"

    return item


@pytest.fixture
def junior_user():
    user = User()
    user.id = str(uuid4())
    user.level_id = 1
    return user


@pytest.fixture
def senior_user():
    user = User()
    user.id = str(uuid4())
    user.level_id = 2
    return user


@pytest.fixture
def session(open_item1, open_item2, closed_item, unconfirmed_item, junior_user, senior_user):
    session = get_db_session(True, None)
    session.add(open_item1)
    session.add(open_item2)
    session.add(closed_item)
    session.add(unconfirmed_item)
    session.add(junior_user)
    session.add(senior_user)
    session.commit()
    return session


def test_get_open_items(session, junior_user, senior_user):
    items = item_handler.get_open_items_for_user(junior_user, 5, True, session)
    assert len(items) == 2

    items = item_handler.get_open_items_for_user(senior_user, 5, True, session)
    assert len(items) == 2


def test_create_item():
    session = get_db_session(True, None)
    item = Item()
    item.content = "Testitem"
    item = item_handler.create_item(item, True, session)
    assert item.id is not None
    assert item.open_reviews == 4
    assert item.open_reviews_level_1 == 4
    assert item.open_reviews_level_2 == 4
    assert item.in_progress_reviews_level_1 == 0
    assert item.in_progress_reviews_level_2 == 0
    assert item.open_timestamp is not None
