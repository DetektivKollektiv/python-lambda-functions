from core_layer.model.review_pair_model import ReviewPair
from core_layer.handler import review_handler
from sqlalchemy import or_


def get_review_pair_from_review(review, session) -> ReviewPair:

    pair = session.query(ReviewPair).filter(
        or_(
            ReviewPair.junior_review_id == review.id,
            ReviewPair.senior_review_id == review.id
        )
    ).first()

    return pair


def compute_difference(pair: ReviewPair) -> float:
    junior_review_average = review_handler.compute_review_result(pair.junior_review.review_answers)
    senior_review_average = review_handler.compute_review_result(pair.senior_review.review_answers)

    return abs(junior_review_average - senior_review_average)


def get_review_pairs_by_item(item_id, session):

    pairs = session.query(ReviewPair).filter(
        ReviewPair.item_id == item_id).all()

    return pairs
