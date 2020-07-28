import logging
from crud.model import Item, ExternalFactCheck, ItemURL, FactChecking_Organization
from crud import operations
from uuid import uuid4

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
    for json_event in event['FactChecks']:
        organization = FactChecking_Organization()
        factcheck = ExternalFactCheck()
        # What is the publishing organization?
        if 'publisher' not in json_event['claimReview'][0]:
            org_name = "Unknown"
        elif 'site' in json_event['claimReview'][0]['publisher']:
            org_name = json_event['claimReview'][0]['publisher']['site']
        elif 'name' in json_event['claimReview'][0]['publisher']:
            org_name = json_event['claimReview'][0]['publisher']['name']
        else:
            org_name = "Unknown"
        # Does the publishing organization already exist?
        # search for url in database
        try:
            organization = operations.get_organization_by_content_db(org_name)
        except Exception:
            # store organization in database
            organization.id = str(uuid4())
            organization.name = org_name
            organization.counter_trustworthy = 0
            organization.counter_not_trustworthy = 0
            try:
                operations.update_object_db(organization)
            except Exception as e:
                logger.error("Could not store Organization. Exception: %s", e, exc_info=True)
        # store factcheck in database
        factcheck.id = str(uuid4())
        factcheck.url = json_event['claimReview'][0]['url']
        factcheck.item_id = event['item']['id']
        factcheck.factchecking_organization_id = organization.id
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
