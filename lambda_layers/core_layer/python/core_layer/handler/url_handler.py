from core_layer.connection_handler import get_db_session
from core_layer.model.url_model import URL, ItemURL


def get_url_by_content(content, is_test, session):
    """Returns an url with the specified content from the database

        Returns
        ------
        url: URL
            An url referenced in an item
        Null, if no url was found
        """
    session = get_db_session(is_test, session)
    url = session.query(URL).filter(URL.url == content).first()
    if url is None:
        raise Exception("No url found.")
    return url


def get_itemurl_by_url_and_item_id(url_id, item_id, is_test, session):
    """Returns the itemurl for an item and url

        Returns
        ------
        itemurl: ItemURL
        Null, if no itemurl was found
        """
    session = get_db_session(is_test, session)
    itemurl = session.query(ItemURL).filter(ItemURL.url_id == url_id,
                                            ItemURL.item_id == item_id).first()
    if itemurl is None:
        raise Exception("No ItemURL found.")
    return itemurl
