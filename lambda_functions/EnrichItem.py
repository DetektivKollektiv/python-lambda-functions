import logging
from crud.model import Item, ExternalFactCheck, ItemURL
from crud import operations

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def update_item(event, context):
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
        operations.update_object_db(item)
    except Exception as e:
        logger.error("Could not update item. Exception: %s", e, exc_info=True)
        raise


def store_factchecks(event, context):
    """stores data related to factchecks

    Parameters
    ----------
    event: dict, required
        FactChecks
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
    factcheck = ExternalFactCheck()
    for json_event in event['FactChecks']:
        factcheck.id = str(uuid4())
        factcheck.url = json_event['claimReview']['url']
        factcheck.item_id = event['item']['id']
        try:
            operations.update_object_db(factcheck)
        except Exception as e:
            logger.error("Could not store factchecks. Exception: %s", e, exc_info=True)
            raise


def store_itemurl(event, context):
    """stores urls referenced in item

    Parameters
    ----------
    event: dict, required
        factchecks

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

    # Store all urls referenced in the item
    url = URL()
    for str_url in event['Claim']['urls']:
        if str_url=="":
            continue
        # search for url in database
        try:
            url = operations.get_url_by_content_db(str_url)
        except Exception:
            # store url in database
            url.id = str(uuid4())
            url.url = str_url
            try:
                operations.update_object_db(url)
            except Exception as e:
                logger.error("Could not store urls. Exception: %s", e, exc_info=True)
                raise
        # store itemurl in database
        itemurl = ItemURL()
        itemurl.id = str(uuid4())
        itemurl.item_id = event['item']['id']
        itemurl.url_id = url.id
        try:
            operations.update_object_db(itemurl)
        except Exception as e:
            logger.error("Could not store itemurls. Exception: %s", e, exc_info=True)
        raise
