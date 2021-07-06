import pytest
from uuid import uuid4
from core_layer.connection_handler import get_db_session
from core_layer.model.item_model import Item
from core_layer.model.user_model import User
from core_layer.model.level_model import Level
from archive_service.post_comment_on_item import post_comment_on_item


@pytest.fixture
def item_id():
    return str(uuid4())

@pytest.fixture
def user_id():
    return str(uuid4())

@pytest.fixture
def event(item_id, user_id):
    return {
        "body": {
            "user_id": user_id,
            "item_id": item_id,
            "qualitative_comment": "Comment from event"
        }
    }

@pytest.fixture
def session(item_id, user_id):
    session = get_db_session(True, None)

    item_obj = new_func(item_id)
    user_obj = User(id = user_id)
    level_1_obj = Level(id = 1)
    session.add_all([item_obj, level_1_obj, user_obj])
    session.commit()
    return session

def new_func(item_id):
    item_obj = Item(id = item_id)
    return item_obj


def test_post_comment_on_item(event, item_id, user_id, session):

    post_comment_on_item(event, is_test = True, session = session)
    assert session.query(Item).all()[0].comments[0].comment == "Comment from event"