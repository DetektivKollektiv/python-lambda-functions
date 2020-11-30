from core_layer.model import User
from sqlalchemy.orm import Session
from core_layer.connection_handler import get_db_session
from core_layer import helper
from uuid import uuid4


def get_user_by_id(id, is_test, session):
    """Returns a user by their id

    Parameters
    ----------
    id: str, required
        The id of the user

    Returns
    ------
    user: User
        The user
    """

    session = get_db_session(is_test, session)
    user = session.query(User).get(id)
    return user
