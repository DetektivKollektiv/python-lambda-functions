from core_layer.connection_handler import get_db_session
from core_layer.model.tag_model import Tag, ItemTag


def get_tags_by_itemid(item_id, is_test, session):
    """Returns the tags for an item

        Returns
        ------
        tags: Tag[]
        Null, if no tag was found
    """
    session = get_db_session(is_test, session)
    tags = session.query(Tag).\
        join(ItemTag).\
        filter(ItemTag.item_id == item_id).\
        filter(ItemTag.tag_id == Tag.id).\
        all()
    return tags


def get_tag_by_content(content, is_test, session):
    """Returns an tag with the specified content from the database

        Returns
        ------
        tag: Tag
            A tag of an item
        Null, if no tag was found
        """
    session = get_db_session(is_test, session)
    tag = session.query(Tag).filter(Tag.tag == content).first()
    return tag


def get_itemtag_by_tag_and_item_id(tag_id, item_id, is_test, session):
    """Returns the itemtag for an item and tag

        Returns
        ------
        itemtag: ItemTag
        Null, if no itemtag was found
    """
    session = get_db_session(is_test, session)
    itemtag = session.query(ItemTag).filter(ItemTag.tag_id == tag_id,
                                                  ItemTag.item_id == item_id).first()
    return itemtag
