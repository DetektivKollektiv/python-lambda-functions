from core_layer.connection_handler import get_db_session
from core_layer.model.review_pair_model import ReviewPair
from core_layer.handler import review_handler
from sqlalchemy import or_


def get_review_pair_from_review(review, is_test, session) -> ReviewPair:
    session = get_db_session(is_test, session)

    pair = session.query(ReviewPair).filter(
        or_(
            ReviewPair.junior_review_id == review.id,
            ReviewPair.senior_review_id == review.id
        )
    ).first()

    return pair


def compute_variance(pair: ReviewPair) -> float:
    junior_review_average = review_handler.compute_review_result(
        pair.junior_review.review_answers)
    senior_review_average = review_handler.compute_review_result(
        pair.senior_review.review_answers)

    return abs(junior_review_average - senior_review_average)


def get_review_pairs_by_item(item_id, is_test, session):
    session = get_db_session(is_test, session)

    pairs = session.query(ReviewPair).filter(
        ReviewPair.item_id == item_id).all()

    return pairs
