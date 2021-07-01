from core_layer.model.item_model import Item
from core_layer.handler import item_handler
from core_layer.db_handler import Session


def test_create_item():
    with Session() as session:
        item = Item()
        item.content = "Testitem"
        item = item_handler.create_item(item, session)
        assert item.id is not None
        assert item.open_reviews == 4
        assert item.open_reviews_level_1 == 4
        assert item.open_reviews_level_2 == 4
        assert item.in_progress_reviews_level_1 == 0
        assert item.in_progress_reviews_level_2 == 0
        assert item.open_timestamp is not None
