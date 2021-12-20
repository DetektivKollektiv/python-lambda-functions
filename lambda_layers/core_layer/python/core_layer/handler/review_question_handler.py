from typing import List
from core_layer.model import ReviewQuestion


def get_all_review_questions_db(session):
    """Returns all review questions from the database

    Returns
    ------
    review_questions: ReviewQuestion[]
        The review questions
    """

    review_questions = session.query(ReviewQuestion).all()
    return review_questions


def get_all_parent_questions(item_type_id, session) -> List[ReviewQuestion]:
    """Returns all parent questions from db

    Returns
    ------
    review_questions: ReviewQuestion[]
        The review questions

    """

    review_questions = session.query(ReviewQuestion).filter(
        ReviewQuestion.parent_question_id == None, ReviewQuestion.item_type_id == item_type_id).all()
    return review_questions


def get_all_child_questions(parent_question_id, session) -> List[ReviewQuestion]:
    review_questions = session.query(ReviewQuestion).filter(
        ReviewQuestion.parent_question_id == parent_question_id).all()
    return review_questions


def get_review_question_by_id(question_id, session):
    """Returns a review question for a given id from the database

    Returns
    ------
    question: ReviewQuestion
        The review question
    """

    question = session.query(ReviewQuestion).filter(
        ReviewQuestion.id == question_id
    ).one()

    return question


def get_review_questions_by_item_type_id(item_type_id, session) -> List[ReviewQuestion]:
    """Returns all review questions for a given item type from the database

    Returns
    ------
    review_questions: ReviewQuestion[]
        The review questions
    """
    review_questions = session.query(ReviewQuestion).filter(
        ReviewQuestion.item_type_id == item_type_id).all()

    return review_questions
