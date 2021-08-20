import logging
import json

from core_layer.db_handler import Session
from core_layer import helper
from core_layer.handler import item_handler

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_item(event, context):
    helper.log_method_initiated("Get closed item", event, logger)

    with Session() as session:
        try:
            # Get item id from path params
            item_id = event['pathParameters']['item_id']
        except KeyError:
            return helper.get_text_response(400, 'Could not read item id from path params', event)
        item = item_handler.get_item_by_id(item_id, session)
        if item is None:
            return helper.get_text_response(404, 'No item found with the specified id', event)
        if item.status != 'closed':
            return helper.get_text_response(403, 'You are not allowed to access an item, that has not been closed', event)

        response = {
            "statusCode": 200,
            'headers': {"content-type": "application/json; charset=utf-8"},
            "body": json.dumps(item.to_dict(True, True, True, True))
        }
        return helper.set_cors(response, event)
