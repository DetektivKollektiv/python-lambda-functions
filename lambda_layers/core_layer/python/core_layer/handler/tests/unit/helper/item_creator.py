from core_layer.model import Item


def create_item(id) -> Item:
    item = Item()

    item.id = id

    return item
