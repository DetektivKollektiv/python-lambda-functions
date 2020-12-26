# External imports
import logging
import json
from uuid import uuid4
# Helper imports
from core_layer import helper
from core_layer.connection_handler import get_db_session
from core_layer.handler import item_handler, tag_handler


def get_tags_for_item(event, context, is_test=False, session=None):

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    helper.log_method_initiated("Get tags by item id", event, logger)

    if session is None:
        session = get_db_session(is_test, None)

    try:
        # get id (str) from path
        id = event['pathParameters']['item_id']

        try:
            tag_objects = tag_handler.get_tags_by_itemid(id, is_test, session)

            tags = []
            for obj in tag_objects:
                tags.append(obj.to_dict()['tag'])
        except Exception as e:
            response = {
                "statusCode": 404,
                "body": "No tags found. Exception: {}".format(e)
            }
    except Exception as e:
        response = {
            "statusCode": 400,
            "body": "Could not get item ID. Check HTTP POST payload. Exception: {}".format(e)
        }
    response = {
        "statusCode": 200,
        'headers': {"content-type": "application/json; charset=utf-8"},
        "body": {"Tags": tags}
    }

    response_cors = helper.set_cors(response, event, is_test)
    return response_cors
