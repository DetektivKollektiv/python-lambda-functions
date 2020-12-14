from uuid import uuid4
from core_layer.connection_handler import get_db_session
from core_layer.model.review_answer_model import ReviewAnswer
from core_layer.model.review_model import Review


def create_review_answer(review_answer, is_test, session):
    """Inserts a new review answer into the database

    Parameters
    ----------
    review_answer: ReviewAnswer, required
        The review answer to be inserted

    Returns
    ------
    review_answer: reviewAnswer
        The inserted review answer
    """

    session = get_db_session(is_test, session)

    review_answer.id = str(uuid4())
    session.add(review_answer)
    session.commit()
    session.expire_all()

    return review_answer


def get_partner_answer(partner_review: Review, question_id, is_test, session) -> ReviewAnswer:
    session = get_db_session(is_test, session)

    review_answer = session.query(ReviewAnswer).filter(
        ReviewAnswer.review_id == partner_review.id,
        ReviewAnswer.review_question_id == question_id).first()

    return review_answer
