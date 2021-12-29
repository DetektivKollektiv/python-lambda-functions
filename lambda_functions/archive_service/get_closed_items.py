import logging
import json
import traceback

from core_layer.db_handler import Session
from core_layer import helper
from core_layer.handler import item_handler

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_closed_items(event, context):

    helper.log_method_initiated("Get all closed items", event, logger)

    with Session() as session:
        plugin_call = False
        try:
            url = event["queryStringParameters"]['url']
            logger.info("Found url in queryparams")
            plugin_call = True
        except:
            url = None
            logger.info("No url found in queryparams")
            pass

        try:
            # Get all closed items
            print("\n \n \n Getting items \n \n \n")

            if url:
                items = item_handler.get_closed_items_by_url(url, session)
            else:
                items = item_handler.get_all_closed_items(session)

            if len(items) == 0:
                response = {
                    "statusCode": 204,
                    "body": "No closed items found"
                }
            else:
                items_list = []
                for item in items:
                    items_list.append(item.to_dict(
                        with_tags=True, with_warnings=True))

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

    response_cors = helper.set_cors(response, event, plugin_call)
    return response_cors
