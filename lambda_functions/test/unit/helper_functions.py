import json
from uuid import uuid4
import test.unit.event_creator as event_creator
import app
from crud.model import ReviewAnswer, Review
import review_answer_handler


def create_answers_for_review(review: Review, answer: int, session):
    question_id = None
    for i in range(7):
        next_question_event = event_creator.get_next_question_event(
            review.id, question_id)
        response = app.get_review_question(
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

        response = review_answer_handler.create_review_answer(
            review_answer_event, None, True, session)
        assert response['statusCode'] == 201
