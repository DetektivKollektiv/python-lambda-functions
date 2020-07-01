import sys
import logging
sys.path.append("..")
from crud.model import Item
from crud import operations

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def enrich_item(event, context):
    """stores data related to item

    Parameters
    ----------
    event: dict, required
        item

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: application/json

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    print(event)

    # Parse event dict to Item object
    item = Item()
    json_event = event['item']
    for key in json_event:
        setattr(item, key, json_event[key])

    try:
        operations.update_item_db(item)
    except Exception as e:
        logger.error("Could not update item. Exception: %s", e, exc_info=True)
        raise
