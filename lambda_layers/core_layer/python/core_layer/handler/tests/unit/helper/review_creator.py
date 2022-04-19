from core_layer.model import Review
from datetime import datetime


def create_review(id: int, item_id: str, user_id: str = None, status: str = None, finish_time=None) -> Review:
    review = Review()

    review.id = id
    review.item_id = item_id
    review.user_id = user_id
    review.status = status
    if finish_time == None:
        review.finish_timestamp = datetime.now()
    else:
        review.finish_timestamp = finish_time

    return review
