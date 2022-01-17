from core_layer.db_handler import update_object
from core_layer.model.tag_model import Tag, ItemTag
from uuid import uuid4


def get_tags_by_itemid(item_id, session):
    """Returns the tags for an item

        Returns
        ------
        tags: Tag[]
        Null, if no tag was found
    """

    tags = session.query(Tag).\
        join(ItemTag).\
        filter(ItemTag.item_id == item_id).\
        filter(ItemTag.tag_id == Tag.id).\
        all()
    return tags


def get_tag_by_content(content, session):
    """Returns an tag with the specified content from the database

        Returns
        ------
        tag: Tag
            A tag of an item
        Null, if no tag was found
        """

    tag = session.query(Tag).filter(Tag.tag == content).first()
    return tag


def get_itemtag_by_tag_and_item_id(tag_id, item_id, session):
    """Returns the itemtag for an item and tag

        Returns
        ------
        itemtag: ItemTag
        Null, if no itemtag was found
    """

    itemtag = session.query(ItemTag).filter(ItemTag.tag_id == tag_id,
                                            ItemTag.item_id == item_id).first()
    return itemtag


def store_tag_for_item(item_id, str_tag, session, review_id=None):
    # search for tag in database
    tag = get_tag_by_content(str_tag, session)
    if tag is None:
        # store tag in database
        tag = Tag()
        tag.id = str(uuid4())
        tag.tag = str_tag
        update_object(tag, session)
    # store item tag in database
    itemtag = ItemTag()
    itemtag.id = str(uuid4())
    itemtag.item_id = item_id
    itemtag.tag_id = tag.id
    if review_id is not None:
        itemtag.review_id = review_id
    update_object(itemtag, session)


def delete_itemtag_by_tag_and_review_id(tag: str, review_id: str, session):
    """
    Deletes the itemtag for an item and tag
    """
    itemtag = session.query(ItemTag).join(Tag).filter(Tag.tag == tag,
                                                      ItemTag.review_id == review_id).one()
    if itemtag is not None:
        session.delete(itemtag)
        session.commit()


def get_all_tags(session):
    """Returns all tags

    Returns:
        [Tag]: A list of tag objects
    """

    query = session.query(Tag)
    return query.all()


def get_item_tags_by_review_id(review_id: str, session):
    """Returns all tags that belong to the review with the specified id

    Args:
        review_id (str): The review id
        session ([type]): An SQL Alchemy session object
    """
    return session.query(ItemTag).filter(ItemTag.review_id == review_id).all()
