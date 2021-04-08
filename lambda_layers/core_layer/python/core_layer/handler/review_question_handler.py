import random

from core_layer.connection_handler import get_db_session
from core_layer.handler import review_handler
from core_layer.model import Review, ReviewAnswer, ReviewQuestion


def get_all_review_questions_db(is_test, session):
    """Returns all review questions from the database

    Returns
    ------
    review_questions: ReviewQuestion[]
        The review questions
    """

    session = get_db_session(is_test, session)
    review_questions = session.query(ReviewQuestion).all()
    return review_questions


def get_all_parent_questions(item_type_id, is_test, session) -> [ReviewQuestion]:
    """Returns all parent questions from db

    Returns
    ------
    review_questions: ReviewQuestion[]
        The review questions

    """

    session = get_db_session(is_test, session)
    review_questions = session.query(ReviewQuestion).filter(
        ReviewQuestion.parent_question_id == None, ReviewQuestion.item_type_id == item_type_id).all()
    return review_questions


def get_all_child_questions(parent_question_id, is_test, session) -> [ReviewQuestion]:
    session = get_db_session(is_test, session)
    review_questions = session.query(ReviewQuestion).filter(
        ReviewQuestion.parent_question_id == parent_question_id).all()
    return review_questions


def get_review_question_by_id(question_id, is_test, session):
    """Returns a review question for a given id from the database

    Returns
    ------
    question: ReviewQuestion
        The review question
    """

    session = get_db_session(is_test, session)

    question = session.query(ReviewQuestion).filter(
        ReviewQuestion.id == question_id
    ).one()

    return question


def get_review_questions_by_item_type_id(item_type_id, is_test, session):
    """Returns all review questions for a given item type from the database

    Returns
    ------
    review_questions: ReviewQuestion[]
        The review questions
    """

    session = get_db_session(is_test, session)
    review_questions = session.query(ReviewQuestion).filter(
        ReviewQuestion.item_type_id == item_type_id).all()

    return review_questions
