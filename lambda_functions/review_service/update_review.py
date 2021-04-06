import logging
import json
import traceback
from core_layer import helper
from core_layer import connection_handler
from core_layer.handler import user_handler, item_handler, review_handler, review_answer_handler
from . import notifications


def update_review(event, context, is_test=False, session=None):
    """Updates an existing review

    Args:
        event: AWS API Gateway event
        context ([type]): [description]
        is_test (bool, optional): Whether the function is executed in test mode. Defaults to False.
        session (optional): An sql alchemy session. Defaults to None.

    Returns
    ------
    - Status code 200, 400, 404 or 500 (Created)
    - The updated review
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    helper.log_method_initiated("Create Review", event, logger)

    if session == None:
        session = connection_handler.get_db_session(False, None)

    try:
        user_id = helper.cognito_id_from_event(event)
        user = user_handler.get_user_by_id(user_id, is_test, session)

        body = json.loads(event['body']) if isinstance(
            event['body'], str) else event['body']

        if 'id' not in body:
            response = {
                "statusCode": 400,
                "body": "Bad request. Please provide a review id"
            }
            response_cors = helper.set_cors(response, event, is_test)
            return response_cors

        review = review_handler.get_review_by_id(
            body['id'], is_test, session)

        if review.user_id != user.id:
            response = {
                "statusCode": 403,
                "body": "Forbidden. You are not allowed to access other users reviews."
            }
            response_cors = helper.set_cors(response, event, is_test)
            return response_cors
        # If review is set closed
        if 'status' in body and body['status'] == 'closed':
            review = review_handler.close_review(review, is_test, session)
            if review.item.status == 'closed':
                notifications.notify_users(is_test, session, review.item)
            response = {
                "statusCode": 200,
                "body": json.dumps(review.to_dict_with_questions_and_answers())
            }

        # If answers are appended
        elif 'questions' in body:
            for question in body['questions']:
                if 'answer_value' in question:
                    answer_value = question['answer_value']
                else:
                    response = {
                        "statusCode": 400,
                        "body": "Bad request. Please provide a valid body"
                    }
                    response_cors = helper.set_cors(response, event, is_test)
                    return response_cors

                if answer_value is not None:
                    # Check if conditionality is met
                    if question['parent_question_id'] is not None:
                        parent_answer = review_answer_handler.get_parent_answer(
                            question['answer_id'], is_test, session)
                        if parent_answer.answer > question['upper_bound'] or parent_answer.answer < question['lower_bound']:
                            response = {
                                "statusCode": 400,
                                "body": "Bad request. Please adhere to conditionality of questions."
                            }
                            response_cors = helper.set_cors(
                                response, event, is_test)
                            return response_cors
                    # Update answer in db
                    review_answer_handler.set_answer_value(
                        question['answer_id'], question['answer_value'], is_test, session)

            response = {
                "statusCode": 200,
                "body": json.dumps(review.to_dict_with_questions_and_answers())
            }

        else:
            response = {
                "statusCode": 400,
                "body": "Bad request"
            }

    except Exception:
        response = {
            "statusCode": 500,
            "body": "Internal server error/uncaught exception. Stacktrace: {}".format(traceback.format_exc())
        }

    response_cors = helper.set_cors(response, event, is_test)
    return response_cors
