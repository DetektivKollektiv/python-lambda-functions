from core_layer.connection_handler import get_db_session
from core_layer.model.keyphrase_model import Keyphrase, ItemKeyphrase


def get_phrases_by_itemid_db(item_id, is_test, session):
    """Returns the key phrases for an item

        Returns
        ------
        phrases: Keyphrase[]
        Null, if no entity was found
    """
    session = get_db_session(is_test, session)
    phrases = session.query(Keyphrase).\
        join(ItemKeyphrase).\
        filter(ItemKeyphrase.item_id == item_id).\
        filter(ItemKeyphrase.keyphrase_id == Keyphrase.id).\
        all()
    return phrases


def get_phrase_by_content(content, is_test, session):
    """Returns a keyphrase with the specified content from the database

        Returns
        ------
        keyphrase: Keyphrase
            A key phrase of an item
        Null, if no key phrase was found
        """
    session = get_db_session(is_test, session)
    phrase = session.query(Keyphrase).filter(
        Keyphrase.phrase == content).first()
    if phrase is None:
        raise Exception("No key phrase found.")
    return phrase


def get_itemphrase_by_phrase_and_item_id(phrase_id, item_id, is_test, session):
    """Returns the itemkeyphrase for an item and keyphrase

        Returns
        ------
        itemphrase: ItemKeyphrase
        Null, if no itemphrase was found
    """
    session = get_db_session(is_test, session)
    itemphrase = session.query(ItemKeyphrase).filter(ItemKeyphrase.keyphrase_id == phrase_id,
                                                     ItemKeyphrase.item_id == item_id).first()
    if itemphrase is None:
        raise Exception("No ItemKeyphrase found.")
    return itemphrase
