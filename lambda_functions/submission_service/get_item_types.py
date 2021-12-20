import logging
import json
import traceback
from core_layer import helper
from core_layer.db_handler import Session
from core_layer.handler import item_type_handler


def get_item_types(event, context):
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    helper.log_method_initiated("Get Item Types", event, logger)

    with Session() as session: 

        try:
            item_types = item_type_handler.get_all_item_types(session)

            if item_types == None:
                response = {
                    "statusCode": 201,
                    'headers': {"content-type": "application/json; charset=utf-8"},
                    "body": []
                }
            else:
                response = {
                    "statusCode": 200,
                    'headers': {"content-type": "application/json; charset=utf-8"},
                    "body": json.dumps([item_type.to_dict() for item_type in item_types])
                }

        except Exception:
            response = {
                "statusCode": 500,
                "body": "Could not get item types. Stacktrace: {}".format(traceback.format_exc())
            }

        return helper.set_cors(response, event)
