from core_layer.model import Review
from core_layer.helper import get_date_time, get_date_time_now
from datetime import datetime


def create_review(id: int, item_id: str, user_id: str, status: str, finish_time=None) -> Review:
    review = Review()

    review.id = id
    review.item_id = item_id
    review.user_id = user_id
    review.status = status
    if finish_time == None:
        review.finish_timestamp = get_date_time_now()
    else:
        review.finish_timestamp = get_date_time(finish_time, True)
        
    return review
