from core_layer.model.entity_model import Entity, ItemEntity


def get_entities_by_itemid(item_id, session):
    """Returns the entities for an item

        Returns
        ------
        entities: Entity[]
        Null, if no entity was found
    """

    entities = session.query(Entity).\
        join(ItemEntity).\
        filter(ItemEntity.item_id == item_id).\
        filter(ItemEntity.entity_id == Entity.id).\
        all()
    return entities


def get_entity_by_content(content, session):
    """Returns an entity with the specified content from the database

        Returns
        ------
        entity: Entity
            An entity of an item
        Null, if no entity was found
        """

    entity = session.query(Entity).filter(Entity.entity == content).first()
    if entity is None:
        raise Exception("No entity found.")
    return entity


def get_itementity_by_entity_and_item_id(entity_id, item_id, session):
    """Returns the itementity for an item and entity

        Returns
        ------
        itementity: ItemEntity
        Null, if no itementity was found
    """

    itementity = session.query(ItemEntity).filter(ItemEntity.entity_id == entity_id,
                                                  ItemEntity.item_id == item_id).first()
    if itementity is None:
        raise Exception("No ItemEntity found.")
    return itementity
