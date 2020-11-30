from uuid import uuid4
from core_layer import helper
from core_layer.model import Review, ReviewPair


def accept_item_db(user, item, is_test, session):
    """Accepts an item for review

    Parameters
    ----------
    user: User
        The user that reviews the item
    item: Item
        The item to be reviewed by the user

    Returns
    ------
    item: Item
        The case to be assigned to the user
    """
    # If a ReviewInProgress exists for the user, return
    try:
        session.query(Review).filter(
            Review.user_id == user.id, Review.status == "in_progress", Review.item_id == item.id).one()
        return item
    except:
        pass

    # If the amount of reviews in progress equals the amount of reviews needed, raise an error
    if item.in_progress_reviews_level_1 >= item.open_reviews_level_1:
        if user.level_id > 1:
            if item.in_progress_reviews_level_2 >= item.open_reviews_level_2:
                raise Exception(
                    'Item cannot be accepted since enough other detecitves are already working on the case')
        else:
            raise Exception(
                'Item cannot be accepted since enough other detecitves are already working on the case')
    # Create a new ReviewInProgress
    rip = Review()
    rip.id = str(uuid4())
    rip.item_id = item.id
    rip.user_id = user.id
    rip.start_timestamp = helper.get_date_time_now(is_test)
    rip.status = "in_progress"

    # If a user is a senior, the review will by default be a senior review,
    # except if no senior reviews are needed
    if user.level_id > 1 and item.open_reviews_level_2 > item.in_progress_reviews_level_2:
        rip.is_peer_review = True
        item.in_progress_reviews_level_2 = item.in_progress_reviews_level_2 + 1

        # Check if a pair with open senior review exists
        pair_found = False
        for pair in item.review_pairs:
            if pair.senior_review_id == None:
                pair.senior_review_id = rip.id
                pair_found = True
                session.merge(pair)
                break

        # Create new pair, if review cannot be attached to existing pair
        if pair_found == False:
            pair = ReviewPair()
            pair.id = str(uuid4())
            pair.senior_review_id = rip.id
            item.review_pairs.append(pair)
            session.merge(pair)

    # If review is junior review
    else:
        rip.is_peer_review = False
        item.in_progress_reviews_level_1 = item.in_progress_reviews_level_1 + 1

        # Check if a pair with open junior review exists
        pair_found = False
        for pair in item.review_pairs:
            if pair.junior_review_id == None:
                pair.junior_review_id = rip.id
                pair_found = True
                session.merge(pair)
                break

        # Create new pair, if review cannot be attached to existing pair
        if pair_found == False:
            pair = ReviewPair()
            pair.id = str(uuid4())
            pair.junior_review_id = rip.id
            item.review_pairs.append(pair)
            session.merge(pair)

    session.add(rip)
    session.merge(item)
    session.commit()
    return rip
