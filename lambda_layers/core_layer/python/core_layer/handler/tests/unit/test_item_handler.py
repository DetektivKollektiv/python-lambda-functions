import pytest
from core_layer.model.item_model import Item
from core_layer.model.user_model import User
from core_layer.model.item_type_model import ItemType
from core_layer.handler import item_handler
from helper import review_answer_creator
from core_layer.connection_handler import get_db_session
from uuid import uuid4


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
