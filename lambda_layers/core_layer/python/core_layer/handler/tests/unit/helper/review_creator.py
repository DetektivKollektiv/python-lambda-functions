from uuid import uuid4
from core_layer.model import Review


def create_review(id, item_id) -> Review:
    review = Review()

    review.id = id
    review.item_id = item_id

    return review
