import random
import statistics
import logging
from core_layer.model.item_model import Item
from core_layer.model.review_model import Review
from sqlalchemy.orm import Session
from core_layer.connection_handler import get_db_session
from core_layer import helper
from core_layer.handler import review_pair_handler
from uuid import uuid4


def get_all_items(is_test, session, params: dict = {}) -> [Item]:
    """Returns all items filtered by the provided params

    Args:
        is_test (bool): True, if the function is run from a test
        session (Session): An SQLAlchemy Session
        params (dict, optional): A dictionary consisting of key-value pairs for filtering. Defaults to an empty dict.

    Returns:
        [Item]: A list of item objects
    """
    session = get_db_session(is_test, session)

    query = session.query(Item)
    if not params:
        return query.all()
    else:
        for key in params:
            query = query.filter(getattr(Item, key) == params[key])
    return query.all()


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


def get_item_by_content(content, is_test, session):
    """Returns an item with the specified content from the database

        Returns
        ------
        item: Item
            The item
        Null, if no item was found
        """
    session = get_db_session(is_test, session)
    item = session.query(Item).filter(Item.content == content).first()
    if item is None:
        raise Exception("No item found.")
    return item


def create_item(item, is_test, session):
    """Inserts a new item into the database

    Parameters
    ----------
    item: Item, required
        The item to be inserted

    Returns
    ------
    item: Item
        The inserted item
    """
    session = get_db_session(is_test, session)

    item.id = str(uuid4())
    session.add(item)
    session.commit()

    return item


def get_item_by_id(id, is_test, session) -> Item:
    """Returns an item by its id

    Parameters
    ----------
    id: str, required
        The id of the item

    Returns
    ------
    item: Item
        The item
    """
    session = get_db_session(is_test, session)
    try:
        item = session.query(Item).get(id)
        return item

    except Exception:
        logging.exception('Could not get item by id.')
        return None
    # Uncomment to test telegram user notification
    # notifications.notify_telegram_users(is_test, session, item)


def get_open_items_for_user(user, num_items, is_test, session):
    """Retreives a list of open items (in random order) to be reviewed by a user.

    Parameters
    ----------
    user: User
        The user that should receive a case
    num_items: int
        The (maximum) number of open items to be retreived

    Returns
    ------
    items: Item[]
        The list of open items for the user
    """

    session = get_db_session(is_test, session)
    items = []

    # If review in progress exists for user, return the corresponding item(s)
    result = session.query(Review).filter(
        Review.user_id == user.id, Review.status == "in_progress").limit(num_items)
    if result.count() > 0:
        for rip in result:
            item_id = rip.item_id
            item = get_item_by_id(item_id, is_test, session)
            items.append(item)
        # shuffle list order
        random.shuffle(items)
        return items

    if user.level_id > 1:
        # Get open items for senior review
        result = session.query(Item) \
            .filter(Item.open_reviews_level_2 > Item.in_progress_reviews_level_2) \
            .filter(~Item.reviews.any(Review.user_id == user.id)) \
            .filter(Item.status == "open") \
            .order_by(Item.open_timestamp.asc()) \
            .limit(num_items).all()

        # If open items are available, return them
        if len(result) > 0:
            for item in result:
                items.append(item)
            random.shuffle(items)
            return items

    # Get open items for junior review and return them
    result = session.query(Item) \
        .filter(Item.open_reviews_level_1 > Item.in_progress_reviews_level_1) \
        .filter(~Item.reviews.any(Review.user_id == user.id)) \
        .filter(Item.status == "open") \
        .order_by(Item.open_timestamp.asc()) \
        .limit(num_items).all()

    for item in result:
        items.append(item)
    random.shuffle(items)
    return items


def compute_item_result_score(item_id, is_test, session):
    pairs = review_pair_handler.get_review_pairs_by_item(
        item_id, is_test, session)

    average_scores = []
    for pair in list(filter(lambda p: p.is_good, pairs)):
        average_scores.append(pair.variance)

    result = statistics.median(average_scores)
    return result
