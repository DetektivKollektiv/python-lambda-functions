from core_layer.model.external_factcheck_model import ExternalFactCheck
from core_layer.model.item_model import Item


def get_factcheck_by_url_and_item_id(factcheck_url, item_id, session):
    """Returns the factcheck publishing fact checks

        Returns
        ------
        factcheck: ExternalFactCheck
        Null, if no factcheck was found
        """

    factcheck = session.query(ExternalFactCheck).filter(ExternalFactCheck.url == factcheck_url,
                                                        ExternalFactCheck.item_id == item_id).first()
    if factcheck is None:
        raise Exception("No Factcheck found.")
    return factcheck


def get_factcheck_by_itemid(id, session):
    """Returns factchecks referenced by an item id
    Parameters
    ----------
    id: str, required
        The id of the item
    Returns
    ------
    factcheck: ExternalFactCheck
        The first factcheck referenced by the item
        None if no factcheck referenced by the item
    """

    factcheck = session.query(ExternalFactCheck).select_from(Item).\
        join(Item.factchecks).\
        filter(Item.id == id)
    return factcheck.first()
