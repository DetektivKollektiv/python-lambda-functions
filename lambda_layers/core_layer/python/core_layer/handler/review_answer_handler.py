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


def set_answer_value(answer_id: str, answer_value: int, is_test, session) -> ReviewAnswer:
    session = get_db_session(is_test, session)
    answer = ReviewAnswer()
    answer = session.get(ReviewAnswer, answer_id)
    answer.answer = answer_value
    session.merge(answer)
    session.commit()
    return answer


def get_answer_by_id(answer_id: str, is_test, session) -> ReviewAnswer:
    """Gets a review answer by id

    Args:
        answer_id (str): The id of the answer to get
        is_test (bool): Whether the function is run in test mode
        session ([type]): A session

    Returns:
        ReviewAnswer: The review answer with the specified id. Returns None if no answer was found.
    """

    session = get_db_session(is_test, session)

    answer = session.get(ReviewAnswer, answer_id)
    return answer


def get_parent_answer(answer_id, is_test, session) -> ReviewAnswer:
    """Gets the answer object corresponding to the parent question of the given answer

    Args:
        answer_id (str): The answer id
        is_test (bool): Whether the function is run in test mode
        session ([type]): A session

    Returns:
        ReviewAnswer: The answer of the parent question of the given answer in the same review
    """
    session = get_db_session(is_test, session)
    answer = ReviewAnswer()
    answer = session.get(ReviewAnswer, answer_id)
    parent_answer = session.query(ReviewAnswer).filter(ReviewAnswer.review_question_id ==
                                                       answer.review_question.parent_question_id, ReviewAnswer.review_id == answer.review_id).one()
    return parent_answer
