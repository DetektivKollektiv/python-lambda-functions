import logging
import json

from core_layer.connection_handler import get_db_session
from core_layer.handler import item_handler
from core_layer.model import Item
from core_layer import helper

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_items(event, context, is_test=False, session=None):
    """Returns the requested items. 

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        #api-gateway-simple-proxy-for-lambda-input-format
        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: application/json

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """
    helper.log_method_initiated("Get items", event, logger)

    if session is None:
        session = get_db_session(is_test, session)

    if 'queryStringParameters' in event:
        params = event['queryStringParameters']

        for param in params:
            if hasattr(Item, param) is False:
                response = {
                    "statusCode": 400,
                    "body": "Could not get items. Query params do not match item model."
                }
                response_cors = helper.set_cors(response, event, is_test)
                return response_cors
    else:
        params = None

    items = item_handler.get_all_items(is_test, session, params=params)

    items_list = []

    for item in items:
        items_list.append(item.to_dict())

    response = {
        "statusCode": 200,
        'headers': {"content-type": "application/json; charset=utf-8"},
        "body": json.dumps(items_list)
    }
    response_cors = helper.set_cors(response, event, is_test)
    return response_cors
