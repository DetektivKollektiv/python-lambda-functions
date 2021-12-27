import random
import statistics
import logging
from typing import List
from typing import Dict
from core_layer.model.item_model import Item
from core_layer.model.review_model import Review
from core_layer.model.url_model import URL, ItemURL
from core_layer.handler import review_pair_handler, review_handler
from uuid import uuid4


def get_all_items(session, params: dict = {}) -> List[Item]:
    """Returns all items filtered by the provided params

    Args:
        session (Session): An SQLAlchemy Session
        params (dict, optional): A dictionary consisting of key-value pairs for filtering. Defaults to an empty dict.

    Returns:
        [Item]: A list of item objects
    """

    query = session.query(Item)
    if not params:
        return query.all()
    else:
        for key in params:
            query = query.filter(getattr(Item, key) == params[key])
    return query.all()


def get_all_closed_items(session):
    """Gets all closed items

    Returns
    ------
    items: Item[]
        The closed items
    """

    items = session.query(Item).filter(Item.status == 'closed').all()
    return items


def get_item_by_content(content, session):
    """Returns an item with the specified content from the database

        Returns
        ------
        item: Item
            The item
        Null, if no item was found
        """
    item = session.query(Item).filter(Item.content == content).first()
    if item is None:
        raise Exception("No item found.")
    return item


def create_item(item, session):
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

    item.id = str(uuid4())
    session.add(item)
    session.commit()

    return item


def get_item_by_id(id, session) -> Item:
    """Returns an item by its id.

    Parameters
    ----------
    id: str, required

    Returns
    ------
    item: Item

    """

    try:
        item = session.query(Item).get(id)
        return item

    except Exception:
        logging.exception('Could not get item by id.')
        return None
    # Uncomment to test telegram user notification
    # notifications.notify_telegram_users(is_test, session, item)


def get_open_items_for_user(user, num_items, session) -> Dict[List[Item], bool]:
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
    is_open_review: bool
        True, if an open review was found. False, if no open review was found 
    """

    items = []

    # If review in progress exists for user, return the corresponding item(s)
    result = session.query(Review).filter(
        Review.user_id == user.id, Review.status == "in_progress").limit(num_items)
    if result.count() > 0:
        for rip in result:
            item_id = rip.item_id
            item = get_item_by_id(item_id, session)
            items.append(item)
        # shuffle list order
        random.shuffle(items)
        return {'items': items, 'is_open_review': True}

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
            return {'items': items, 'is_open_review': False}

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

    return {'items': items, 'is_open_review': False}


def compute_item_result_score(item_id, session):
    pairs = review_pair_handler.get_review_pairs_by_item(item_id, session)

    average_scores = []
    for pair in list(filter(lambda p: p.is_good, pairs)):
        average_scores.append(review_handler.compute_review_result(
            pair.junior_review.review_answers))
        average_scores.append(review_handler.compute_review_result(
            pair.senior_review.review_answers))
    result = statistics.median(average_scores)
    return result


def get_items_by_url(url, session) -> List[Item]:
    items = session.query(Item).join(Item.urls).join(
        ItemURL.url).filter_by(url=url).all()
    return items
