from core_layer.model.keyphrase_model import Keyphrase, ItemKeyphrase


def get_phrases_by_itemid_db(item_id, session):
    """Returns the key phrases for an item

        Returns
        ------
        phrases: Keyphrase[]
        Null, if no entity was found
    """

    phrases = session.query(Keyphrase).\
        join(ItemKeyphrase).\
        filter(ItemKeyphrase.item_id == item_id).\
        filter(ItemKeyphrase.keyphrase_id == Keyphrase.id).\
        all()
    return phrases


def get_phrase_by_content(content, session):
    """Returns a keyphrase with the specified content from the database

        Returns
        ------
        keyphrase: Keyphrase
            A key phrase of an item
        Null, if no key phrase was found
        """

    phrase = session.query(Keyphrase).filter(
        Keyphrase.phrase == content).first()
    if phrase is None:
        raise Exception("No key phrase found.")
    return phrase


def get_itemphrase_by_phrase_and_item_id(phrase_id, item_id, session):
    """Returns the itemkeyphrase for an item and keyphrase

        Returns
        ------
        itemphrase: ItemKeyphrase
        Null, if no itemphrase was found
    """

    itemphrase = session.query(ItemKeyphrase).filter(ItemKeyphrase.keyphrase_id == phrase_id,
                                                     ItemKeyphrase.item_id == item_id).first()
    if itemphrase is None:
        raise Exception("No ItemKeyphrase found.")
    return itemphrase


def get_all_keyphrases(session):
    """Returns all keyphrases

    Returns:
        [Keyphrase]: A list of Keyphrase objects
    """

    query = session.query(Keyphrase)
    return query.all()
