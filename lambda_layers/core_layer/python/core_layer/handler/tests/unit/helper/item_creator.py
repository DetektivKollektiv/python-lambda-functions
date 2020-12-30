from core_layer.model import Item


def create_item(id, item_type_id) -> Item:
    item = Item()

    item.id = id
    item.item_type_id = item_type_id

    return item
