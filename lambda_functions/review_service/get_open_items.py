import logging
import json
import traceback
from core_layer import helper
from core_layer import connection_handler
from core_layer.handler import user_handler, item_handler


def get_open_items(event, context, is_test=False, session=None):

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    helper.log_method_initiated("Get open items for user", event, logger)

    if session == None:
        session = connection_handler.get_db_session(False, None)

    try:
        # get cognito user id
        id = helper.cognito_id_from_event(event)

        # get number of items from url path
        num_items = int(event['pathParameters']['num_items'])

        user = user_handler.get_user_by_id(id, is_test, session)
        items = item_handler.get_open_items_for_user(
            user, num_items, is_test, session)

        if len(items) < 1:
            response = {
                "statusCode": 404,
                "body": "There are currently no open items for this user."
            }
        else:
            # Transform each item into dict
            items_dict = []
            for item in items:
                items_dict.append(item.to_dict())

            response = {
                "statusCode": 200,
                'headers': {"content-type": "application/json; charset=utf-8"},
                "body": json.dumps(items_dict)
            }

    except Exception:
        response = {
            "statusCode": 400,
            "body": "Could not get user and/or num_items. Check URL path parameters. Stacktrace: {}".format(traceback.format_exc())
        }

    response_cors = helper.set_cors(response, event, is_test)
    return response_cors
