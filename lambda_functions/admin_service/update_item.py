import logging
import json
import traceback
# Helper imports
from core_layer import helper
from core_layer.connection_handler import get_db_session, update_object
# Model imports
from core_layer.model import Item
# Handler imports
from core_layer.handler import item_handler

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def update_item(event, context, is_test=False, session=None):
    """Updates an item. 

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
    helper.log_method_initiated("Update item", event, logger)

    if session is None:
        session = get_db_session(is_test, session)

    item_id = event['pathParameters']['item_id']

    item = item_handler.get_item_by_id(item_id, is_test, session)

    if item is None:
        response = {
            "statusCode": 404,
            "body": "No item found with the specified id."
        }
        response_cors = helper.set_cors(response, event, is_test)
        return response_cors

    body = event['body']
    body = json.loads(body) if isinstance(body, str) else body

    for key in body:
        if hasattr(item, key):
            if not isinstance(body[key], dict) and not isinstance(body[key], list):
                setattr(item, key, body[key])
        else:
            response = {
                "statusCode": 400,
                "body": "Could not update item. Provided input does not match item model."
            }
            response_cors = helper.set_cors(response, event, is_test)
            return response_cors

    item = update_object(item, is_test, session)
    if item is None:
        response = {
            "statusCode": 500,
            "body": "Could not write changes to db. Event id: {}".format(event['requestContext']['requestId'])
        }
        response_cors = helper.set_cors(response, event, is_test)
        return response_cors

    response = {
        "statusCode": 200,
        "body": json.dumps(item.to_dict())
    }
    response_cors = helper.set_cors(response, event, is_test)
    return response_cors
