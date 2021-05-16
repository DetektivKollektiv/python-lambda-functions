from core_layer.connection_handler import get_db_session, update_object
from core_layer.model.tag_model import Tag, ItemTag
from uuid import uuid4


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

def store_tag_for_item(item_id, str_tag, is_test, session):
    # search for tag in database
    tag = get_tag_by_content(str_tag, is_test, session)
    if tag is None:
        # store tag in database
        tag = Tag()
        tag.id = str(uuid4())
        tag.tag = str_tag
        update_object(tag, is_test, session)
    # item tag already exists?
    itemtag = get_itemtag_by_tag_and_item_id(tag.id, item_id, is_test, session)
    if itemtag is None:
        # store item tag in database
        itemtag = ItemTag()
        itemtag.id = str(uuid4())
        itemtag.item_id = item_id
        itemtag.tag_id = tag.id
        update_object(itemtag, is_test, session)
    else:
        # increase tag counter
        itemtag.count += 1
        update_object(itemtag, is_test, session)

def delete_itemtag_by_tag_and_item_id(tag_id, item_id, is_test, session):
    """Deletes the itemtag for an item and tag
    """
    session = get_db_session(is_test, session)
    itemtag = session.query(ItemTag).filter(ItemTag.tag_id == tag_id,
                                                  ItemTag.item_id == item_id).first()
    if itemtag != None:
        session.delete(itemtag)
        session.commit()

def get_all_tags(is_test, session):
    """Returns all tags

    Returns:
        [Tag]: A list of tag objects
    """
    session = get_db_session(is_test, session)

    query = session.query(Tag)
    return query.all()
