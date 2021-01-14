from core_layer.model import Review, User


def create_review(id: int, item_id: str, user_id: str, status: str) -> Review:
    review = Review()

    review.id = id
    review.item_id = item_id
    review.user_id = user_id
    review.status = status
    return review
