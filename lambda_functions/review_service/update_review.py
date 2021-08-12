from core_layer.event_publisher import EventPublisher
from core_layer.handler import user_handler, review_handler, review_answer_handler
from core_layer.db_handler import Session
import logging
import json
import traceback
from core_layer import helper


def update_review(event, context):
    """Updates an existing review

    Args:
        event: AWS API Gateway event
        context ([type]): [description].

    Returns
    ------
    - Status code 200, 400, 404 or 500 (Created)
    - The updated review
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    helper.log_method_initiated("Update Review", event, logger)

    try:
        user_id = helper.cognito_id_from_event(event)
        body = json.loads(event['body']) if isinstance(
            event['body'], str) else event['body']
    except:
        return helper.get_text_response(400, "Malformed request. Please provide a valid request.", event)

    if 'id' not in body:
        return helper.get_text_response(400, "Malformed request. Please provide a review id.", event)

    session = Session()

    try:
        review = review_handler.get_review_by_id(body['id'], session)
    except:
        return helper.get_text_response(404, "No review found. Stacktrace: {}".format(traceback.format_exc()), event)

    try:
        user = user_handler.get_user_by_id(user_id, session)
    except:
        return helper.get_text_response(404, "No user found.", event)

    if review.user_id != user.id:
        return helper.get_text_response(403, "Forbidden.", event)

    # If review is set closed
    if 'status' in body and body['status'] == 'closed':
        try:
            review = review_handler.close_review(review, session)

            if review.item.status == 'closed':
                EventPublisher().publish_event('codetekt.review_service',
                                               'item_closed', {'item_id': review.item.id})

            response = {
                "statusCode": 200,
                "body": json.dumps(review.to_dict_with_questions_and_answers())
            }
            response_cors = helper.set_cors(response, event)
            session.close()
            return response_cors
        except:
            return helper.get_text_response(500, "Internal server error. Stacktrace: {}".format(traceback.format_exc()), event)

    # If answers are appended
    elif 'questions' in body:
        if not isinstance(body['questions'], list):
            return helper.get_text_response(400, "Malformed request. Please provide a valid request.", event)
        for question in body['questions']:
            if 'answer_value' in question:
                answer_value = question['answer_value']
            else:
                return helper.get_text_response(400, "Malformed request. Please provide a valid request.", event)

            if answer_value is not None:
                # Check if conditionality is met
                if question['parent_question_id'] is not None:
                    for q in body['questions']:
                        if q['question_id'] == question['parent_question_id']:
                            parent_question = q
                    parent_answer = review_answer_handler.get_parent_answer(
                        question['answer_id'], session)
                    if parent_question['answer_value'] > question['upper_bound'] or parent_question['answer_value'] < question['lower_bound']:
                        return helper.get_text_response(400, "Bad request. Please adhere to conditionality of questions.", event)
                # Update answer in db
                try:
                    review_answer_handler.set_answer_value(
                        question['answer_id'], question['answer_value'], session)
                except:
                    return helper.get_text_response(500, "Internal server error. Stacktrace: {}".format(traceback.format_exc()), event)

        response = {
            "statusCode": 200,
            "body": json.dumps(review.to_dict_with_questions_and_answers())
        }
        response_cors = helper.set_cors(response, event)
        return response_cors

    else:
        return helper.get_text_response(400, "Bad request. Please adhere to conditionality of questions.", event)
