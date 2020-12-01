from core_layer.connection_handler import get_db_session
from core_layer.model.entity_model import Entity, ItemEntity


def get_entities_by_itemid(item_id, is_test, session):
    """Returns the entities for an item

        Returns
        ------
        entities: Entity[]
        Null, if no entity was found
    """
    session = get_db_session(is_test, session)
    entities = session.query(Entity).\
        join(ItemEntity).\
        filter(ItemEntity.item_id == item_id).\
        filter(ItemEntity.entity_id == Entity.id).\
        all()
    return entities
