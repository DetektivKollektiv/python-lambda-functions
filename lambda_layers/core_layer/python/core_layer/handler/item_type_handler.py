from typing import List
from core_layer.model.item_type_model import ItemType


def get_all_item_types(session) -> List[ItemType]:
    """
    Returns a list of all item types

    Returns
    ------
    item_types: ItemType[]

    """
    item_types = session.query(ItemType).all()

    return item_types
