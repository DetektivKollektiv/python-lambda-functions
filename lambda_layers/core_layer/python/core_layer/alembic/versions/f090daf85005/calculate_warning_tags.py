from core_layer.handler import item_handler
from core_layer.db_handler import Session


def calculate_warning_tags():
    with Session() as session:
        items_to_update = item_handler.get_items_to_calculate_warning_tags(
            session)
        for item in items_to_update:
            item_handler.update_item_warning_tags(item, session)
