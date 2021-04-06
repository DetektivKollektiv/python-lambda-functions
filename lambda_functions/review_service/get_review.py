import logging
import json
import traceback
from core_layer import helper
from core_layer import connection_handler
from core_layer.handler import user_handler, item_handler, review_handler


def get_review(event, context, is_test=False, session=None):
    """Gets a review.

    Parameters
    ----------
    - user_id is retrieved from the event
    - review_id is retrieved from query parameters

    Returns
    ------
    - Status code 200 OK
    - The requested review
    """

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    helper.log_method_initiated("Get Review", event, logger)

    if session == None:
        session = connection_handler.get_db_session(False, None)

    try:
        # get review id from url query params
        review_id = event['pathParameters']['review_id']

        # get cognito id
        user_id = helper.cognito_id_from_event(event)

        # get user from database
        user = user_handler.get_user_by_id(user_id, is_test, session)

        # Try to receive item
        try:
            review = review_handler.get_review_by_id(
                review_id, is_test, session)

            if review.user_id == user.id:
                response = {
                    "statusCode": 200,
                    'headers': {"content-type": "application/json; charset=utf-8"},
                    "body": json.dumps(review.to_dict_with_questions_and_answers())
                }
            else:
                response = {
                    "statusCode": 403,
                    "body": "Forbidden"
                }

        except Exception:
            response = {
                "statusCode": 400,
                "body": "Cannot accept item. Stacktrace: {}".format(traceback.format_exc())
            }

    except Exception:
        response = {
            "statusCode": 400,
            "body": "Could not get user and/or item. Check URL query parameters. Stacktrace: {}".format(traceback.format_exc())
        }

    response_cors = helper.set_cors(response, event, is_test)
    return response_cors
