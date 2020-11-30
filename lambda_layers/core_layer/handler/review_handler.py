from uuid import uuid4
from sqlalchemy import or_
from core_layer.connection_handler import get_db_session
from core_layer import helper
from core_layer.model.review_model import Review
from core_layer.model.review_pair_model import ReviewPair
from core_layer.handler import item_handler


def get_review_by_id(review_id, is_test, session) -> Review:
    session = get_db_session(is_test, session)

    review = session.query(Review).filter(
        Review.id == review_id
    ).one()

    return review


def get_partner_review(review, is_test, session):
    session = get_db_session(is_test, session)

    pair = session.query(ReviewPair).filter(or_(ReviewPair.junior_review_id ==
                                                review.id, ReviewPair.senior_review_id == review.id)) \
        .first()

    try:
        if review.id == pair.junior_review_id:
            return get_review_by_id(pair.senior_review_id, is_test, session)

        if review.id == pair.senior_review_id:
            return get_review_by_id(pair.junior_review_id, is_test, session)
    except:
        return None


def accept_item_db(user, item, is_test, session) -> Review:
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
    session = get_db_session(is_test, session)

    try:
        review = session.query(Review).filter(
            Review.user_id == user.id, Review.status == "in_progress", Review.item_id == item.id).one()
        return review
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
    session.add(rip)
    session.commit()

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

    session.merge(rip)
    session.merge(item)
    session.commit()
    return rip


def compute_review_result(review_answers):
    if(review_answers == None):
        raise TypeError('ReviewAnswers is None!')

    if not isinstance(review_answers, list):
        raise TypeError('ReviewAnswers is not a list')

    if(len(review_answers) <= 0):
        raise ValueError('ReviewAnswers is an empty list')

    answers = (review_answer.answer for review_answer in review_answers)

    return sum(answers) / len(review_answers)


def get_old_reviews_in_progress(is_test, session):
    old_time = helper.get_date_time_one_hour_ago(is_test)
    session = get_db_session(is_test, session)
    rips = session.query(Review).filter(
        Review.start_timestamp < old_time, Review.status == "in_progress").all()
    return rips


def delete_old_reviews_in_progress(rips, is_test, session):
    for rip in rips:
        item = item_handler.get_item_by_id(rip.item_id, is_test, session)
        if rip.is_peer_review == True:
            item.in_progress_reviews_level_2 -= 1
        else:
            item.in_progress_reviews_level_1 -= 1
        session.merge(item)
        session.delete(rip)
    session.commit()
