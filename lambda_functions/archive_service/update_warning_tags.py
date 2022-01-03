from core_layer.handler import item_handler, review_question_handler
from core_layer.db_handler import Session, update_object


def update_warning_tags(event, context):
    with Session() as session:
        items_to_update = item_handler.get_items_to_calculate_warning_tags(
            session)
        for item in items_to_update:
            item_handler.update_item_warning_tags(item, session)
