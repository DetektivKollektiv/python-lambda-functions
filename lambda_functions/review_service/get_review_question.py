import logging
import json
import traceback
from core_layer import helper
from core_layer import connection_handler
from core_layer.handler import user_handler, item_handler, review_handler, review_question_handler


def get_review_question(event, context, is_test=False, session=None):
    """Returns a viable review question.

    Parameters
    ----------
    - review_id is retrieved from query parameters
    - previous_question_id is retrieved from query parameters

    Returns
    ------
    - Status code 200 (OK) --> Returns next question
    - Status code 204 (No Content) --> Review finished
    """

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    helper.log_method_initiated("Get Review Question", event, logger)

    if session == None:
        session = connection_handler.get_db_session(False, None)

    try:
        # get review and user id from event
        review_id = event['queryStringParameters']['review_id']
        review = review_handler.get_review_by_id(review_id, is_test, session)

    except Exception:
        response = {
            "statusCode": 400,
            "body": "Could not get user and/or item. Check URL query parameters. Stacktrace: {}".format(traceback.format_exc())
        }

    # Try getting previous question id from query params. If none is set, set previous_question as None
    try:
        previous_question_id = event['queryStringParameters']['previous_question_id']
        previous_question = review_question_handler.get_review_question_by_id(
            previous_question_id, is_test, session)

    except Exception:
        previous_question = None

    try:
        question = review_question_handler.get_next_question_db(
            review, previous_question, is_test, session)

        if question == None:
            response = {
                "statusCode": 204,
                'headers': {"content-type": "application/json; charset=utf-8"},
                "body": "Cannot return new question, because enough answers are alredy available"
            }
        else:
            response = {
                "statusCode": 200,
                'headers': {"content-type": "application/json; charset=utf-8"},
                "body": json.dumps(question.to_dict_with_answers())
            }
    except Exception:
        response = {
            "statusCode": 400,
            "body": "Could not get next question. Stacktrace: {}".format(traceback.format_exc())
        }

    response_cors = helper.set_cors(response, event, is_test)
    return response_cors
