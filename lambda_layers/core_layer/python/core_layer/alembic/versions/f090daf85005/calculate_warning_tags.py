from core_layer.handler import item_handler
from core_layer.db_handler import Session
from core_layer.model import Item


def calculate_warning_tags():
    with Session() as session:
        items_to_update = session.query(Item).filter(
            Item.status == "closed").all()
        for item in items_to_update:
            item_handler.update_item_warning_tags(item, session)
