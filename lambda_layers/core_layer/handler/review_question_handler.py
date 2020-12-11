import random

from core_layer.connection_handler import get_db_session
from core_layer.model.review_question_model import ReviewQuestion
from core_layer.model.review_answer_model import ReviewAnswer
from core_layer.handler import review_handler


def get_review_question_by_id(question_id, is_test, session):
    session = get_db_session(is_test, session)

    question = session.query(ReviewQuestion).filter(
        ReviewQuestion.id == question_id
    ).one()

    return question


def get_all_review_questions_db(is_test, session):
    """Returns all review answers from the database

    Returns
    ------
    review_questions: ReviewQuestion[]
        The review questions
    """

    session = get_db_session(is_test, session)
    review_questions = session.query(ReviewQuestion).all()
    return review_questions


def get_next_question_db(review, previous_question, is_test, session):
    session = get_db_session(is_test, session)

    if len(review.review_answers) == 7:
        return None

    previous_question_ids = []
    for answer in review.review_answers:
        previous_question_ids.append(answer.review_question_id)

    # Check for conditional question
    if previous_question != None:
        parent_question_found = False
        # Determine relevant parent question
        if len(previous_question.child_questions) > 0:
            parent_question_found = True
            parent_question = previous_question
        if previous_question.parent_question != None:
            parent_question_found = True
            parent_question = previous_question.parent_question

        if parent_question_found:
            parent_answer = session.query(ReviewAnswer).filter(
                ReviewAnswer.review_id == review.id, ReviewAnswer.review_question_id == parent_question.id).one()

            child_questions = parent_question.child_questions

            for child_question in child_questions:
                # Check if question has already been answered
                if child_question.id not in previous_question_ids:
                    # Check answer triggers child question
                    if parent_answer.answer <= child_question.upper_bound and parent_answer.answer >= child_question.lower_bound:
                        return child_question

    partner_review = review_handler.get_partner_review(
        review, is_test, session)

    if partner_review != None:
        partner_review_question_ids = []
        # Get all parent question ids from partner review
        for answer in partner_review.review_answers:
            if answer.review_question.parent_question_id == None:
                partner_review_question_ids.append(answer.review_question_id)
        # Find question
        for question_id in partner_review_question_ids:
            if question_id not in previous_question_ids:
                return get_review_question_by_id(question_id, is_test, session)

    # Check how many questions are still needed
    remaining_questions = 7 - len(review.review_answers)

    # Get all questions
    all_questions = get_all_review_questions_db(is_test, session)
    random.shuffle(all_questions)

    for question in all_questions:
        # Check if question has already been answered
        if question.id not in previous_question_ids:
            # Check if question is a parent question
            if question.parent_question == None:
                # Check if question does not exceed limit with child question
                if question.max_children is not None and remaining_questions > question.max_children:
                    return question

    raise Exception("No question could be returned")
