import logging
import json
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
        # get item id from url query params
        item_id = event['queryStringParameters']['item_id']

        # get cognito id
        user_id = helper.cognito_id_from_event(event)

        # get user and item from the db
        user = user_handler.get_user_by_id(user_id, is_test, session)
        item = item_handler.get_item_by_id(item_id, is_test, session)

        # Try to accept item
        try:
            review = review_handler.accept_item_db(
                user, item, is_test, session)

            response = {
                "statusCode": 201,
                'headers': {"content-type": "application/json; charset=utf-8"},
                "body": json.dumps(review.to_dict())
            }

        except Exception as e:
            response = {
                "statusCode": 400,
                "body": "Cannot accept item. Exception: {}".format(e)
            }

    except Exception as e:
        response = {
            "statusCode": 400,
            "body": "Could not get user and/or item. Check URL query parameters. Exception: {}".format(e)
        }

    response_cors = helper.set_cors(response, event, is_test)
    return response_cors
