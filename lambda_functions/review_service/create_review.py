import logging
import json
import traceback
from core_layer import helper
from core_layer import connection_handler
from core_layer.handler import user_handler, item_handler, review_handler


def create_review(event, context, is_test=False, session=None):
    """Creates a new review.

    Parameters
    ----------
    - user_id is retrieved from the event
    - item_id is retrieved from query parameters

    Returns
    ------
    - Status code 201 (Created)
    - The newly created review
    """

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    helper.log_method_initiated("Create Review", event, logger)

    if session == None:
        session = connection_handler.get_db_session(False, None)

    try:
        # get item id from body
        item_id = json.loads(event['body'])['item_id'] if isinstance(
            event['body'], str) else event['body']['item_id']

        # get cognito id
        user_id = helper.cognito_id_from_event(event)

    except Exception:
        return helper.get_text_response(400, "Malformed request. Please provide a valid request.", event, is_test)

    try:
        # get user and item from the db
        user = user_handler.get_user_by_id(user_id, is_test, session)
    except Exception:
        return helper.get_text_response(404, "No user found.", event, is_test)

    item = item_handler.get_item_by_id(item_id, is_test, session)
    if item is None:
        return helper.get_text_response(404, "No item found.", event, is_test)

    # Try to accept item
    try:
        review = review_handler.create_review(
            user, item, is_test, session)

        response = {
            "statusCode": 201,
            'headers': {"content-type": "application/json; charset=utf-8"},
            "body": json.dumps(review.to_dict_with_questions_and_answers())
        }
        response_cors = helper.set_cors(response, event, is_test)
        return response_cors

    except:
        return helper.get_text_response(500, "Internal server error. Stacktrace: {}".format(traceback.format_exc()), event, is_test)
