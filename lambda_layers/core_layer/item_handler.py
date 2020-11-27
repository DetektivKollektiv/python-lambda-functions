from model import Item
from sqlalchemy import Session
from connection_handler import get_db_session


def get_all_closed_items(is_test, session):
    """Gets all closed items

    Returns
    ------
    items: Item[]
        The closed items
    """

    session = get_db_session(is_test, session)

    items = session.query(Item).filter(Item.status == 'closed').all()
    return items
