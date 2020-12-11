import json
from uuid import uuid4
from . import event_creator
from core_layer.model.review_answer_model import ReviewAnswer
from core_layer.model.review_model import Review
from ...review_service.create_review_answer import create_review_answer
from ...review_service.get_review_question import get_review_question


def create_answers_for_review(review: Review, answer: int, session):
    question_id = None
    for _ in range(7):
        next_question_event = event_creator.get_next_question_event(
            review.id, question_id)
        response = get_review_question(
            next_question_event, None, True, session)
        body = json.loads(response['body'])
        question_id = body['id']

        review_answer = ReviewAnswer()
        review_answer.id = str(uuid4())
        review_answer.review_id = review.id
        review_answer.review_question_id = question_id
        review_answer.answer = answer
        review_answer.comment = 'Test Review Answer'

        review_answer_event = event_creator.get_create_review_answer_event(
            review_answer)

        response = create_review_answer(
            review_answer_event, None, True, session)
        assert response['statusCode'] == 201
