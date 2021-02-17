from core_layer.model import ItemType


def create_item_type(item_type_id, name):
    item_type = ItemType()

    item_type.id = item_type_id
    item_type.name = name

    return item_type
