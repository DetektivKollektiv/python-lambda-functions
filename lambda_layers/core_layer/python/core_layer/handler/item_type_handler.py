from typing import List
from core_layer.connection_handler import get_db_session
from core_layer.model.item_type_model import ItemType


def get_all_item_types(is_test, session) -> List[ItemType]:
    """
    Returns a list of all item types

    Returns
    ------
    item_types: ItemType[]

    """
    session = get_db_session(is_test, session)
    item_types = session.query(ItemType).all()

    return item_types
