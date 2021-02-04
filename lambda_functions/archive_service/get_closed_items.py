import logging
import json
import traceback
from core_layer import helper, connection_handler
from core_layer.handler import item_handler

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_closed_items(event, context, is_test=False, session=None):

    helper.log_method_initiated("Get all closed items", event, logger)

    if session == None:
        session = connection_handler.get_db_session(False, None)

    try:
        # Get all closed items
        items = item_handler.get_all_closed_items(is_test, session)

        if len(items) == 0:
            response = {
                "statusCode": 204,
                "body": "No closed items found"
            }
        else:
            items_list = []

            for item in items:
                items_list.append(item.to_dict_with_tags())
                            
            response = {
                "statusCode": 200,
                'headers': {"content-type": "application/json; charset=utf-8"},
                "body": json.dumps(items_list)
            }

    except Exception:
        response = {
            "statusCode": 400,
            "body": "Could not get closed items. Stacktrace: {}".format(traceback.format_exc())
        }

    response_cors = helper.set_cors(response, event, is_test)
    return response_cors
