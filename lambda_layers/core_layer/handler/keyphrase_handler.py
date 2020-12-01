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
