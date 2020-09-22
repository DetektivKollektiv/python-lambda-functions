import logging
from crud.model import Item, ExternalFactCheck, ItemURL, URL, FactChecking_Organization, Entity, ItemEntity, Sentiment, \
    ItemSentiment, Keyphrase, ItemKeyphrase, Claimant
from crud import operations
from uuid import uuid4
from urllib.parse import urlparse

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def update_item(event, context, is_test=False, session=None):
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

    if session is None:
        session = operations.get_db_session(is_test, session)

    # Parse event dict to Item object
    item = Item()
    json_event = event['item']
    for key in json_event:
        setattr(item, key, json_event[key])

    try:
        operations.update_object_db(item, is_test, session)
    except Exception as e:
        logger.error("Could not update item. Exception: %s", e, exc_info=True)
        raise


def store_factchecks(event, context, is_test=False, session=None):
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

    """

    if session is None:
        session = operations.get_db_session(is_test, session)

    # Parse event dict to Item object
    for json_event in event['FactChecks']:
        if 'claimReview' not in json_event:
            # raise Exception('No claimReview found in factchecks!')
            return
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
        try:
            organization = operations.get_organization_by_content_db(org_name, is_test, session)
        except Exception:
            # store organization in database
            organization.id = str(uuid4())
            organization.name = org_name
            organization.counter_trustworthy = 0
            organization.counter_not_trustworthy = 0
            try:
                operations.update_object_db(organization, is_test, session)
            except Exception as e:
                logger.error("Could not store Organization. Exception: %s", e, exc_info=True)

        factcheck_url = json_event['claimReview'][0]['url']
        factcheck_title = json_event['claimReview'][0]['title']
        item_id = event['item']['id']
        try:
            # Does the factcheck already exist?
            factcheck = operations.get_factcheck_by_url_and_item_db(factcheck_url, item_id, is_test, session)
        except Exception as e:
            # create new factcheck in database
            factcheck.id = str(uuid4())
        # store factcheck in database
        factcheck.url = factcheck_url
        factcheck.title = factcheck_title
        factcheck.item_id = item_id
        factcheck.factchecking_organization_id = organization.id
        try:
            operations.update_object_db(factcheck, is_test, session)
        except Exception as e:
            logger.error("Could not store factchecks. Exception: %s", e, exc_info=True)
            raise


def store_itemurl(event, context, is_test=False, session=None):
    """stores urls referenced in item

    Parameters
    ----------
    event: dict, required
        item
        Claim

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: application/json

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    if session is None:
        session = operations.get_db_session(is_test, session)

    # Store all urls referenced in the item
    for str_url in event['Claim']['urls']:
        if str_url == "":
            continue
        # store claimant derived from url
        domain = urlparse(str_url).hostname
        claimant = Claimant()
        # claimant already exists?
        try:
            claimant = operations.get_claimant_by_name_db(domain, is_test, session)
        except Exception:
            # store claimant in database
            claimant.id = str(uuid4())
            claimant.claimant = domain
            try:
                operations.update_object_db(claimant, is_test, session)
            except Exception as e:
                logger.error("Could not store claimant. Exception: %s", e, exc_info=True)
                raise
        # search for url in database
        url = URL()
        try:
            url = operations.get_url_by_content_db(str_url, is_test, session)
        except Exception:
            # store url in database
            url.id = str(uuid4())
            url.url = str_url
            url.claimant_id = claimant.id
            try:
                operations.update_object_db(url, is_test, session)
            except Exception as e:
                logger.error("Could not store urls. Exception: %s", e, exc_info=True)
                raise
        itemurl = ItemURL()
        # itemurl already exists?
        item_id = event['item']['id']
        try:
            itemurl = operations.get_itemurl_by_url_and_item_db(url.id, item_id, is_test, session)
        except Exception:
            # store itemurl in database
            itemurl.id = str(uuid4())
            itemurl.item_id = item_id
            itemurl.url_id = url.id
            try:
                operations.update_object_db(itemurl, is_test, session)
            except Exception as e:
                logger.error("Could not store itemurls. Exception: %s", e, exc_info=True)
                raise


def store_itementities(event, context, is_test=False, session=None):
    """stores entities of an item

    Parameters
    ----------
    event: dict, required
        item
        Entities

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: application/json

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    if session is None:
        session = operations.get_db_session(is_test, session)

    # Store all entities of the item
    for str_entity in event['Entities']:
        entity = Entity()
        # search for entity in database
        try:
            entity = operations.get_entity_by_content_db(str_entity, is_test, session)
        except Exception:
            # store entity in database
            entity.id = str(uuid4())
            entity.entity = str_entity
            try:
                operations.update_object_db(entity, is_test, session)
            except Exception as e:
                logger.error("Could not store entity. Exception: %s", e, exc_info=True)
                raise
        # store item entity in database
        itementity = ItemEntity()
        # item entity already exists?
        item_id = event['item']['id']
        try:
            itementity = operations.get_itementity_by_entity_and_item_db(entity.id, item_id, is_test, session)
        except Exception:
            itementity.id = str(uuid4())
            itementity.item_id = item_id
            itementity.entity_id = entity.id
            try:
                operations.update_object_db(itementity, is_test, session)
            except Exception as e:
                logger.error("Could not store item entity. Exception: %s", e, exc_info=True)
                raise


def store_itemsentiment(event, context, is_test=False, session=None):
    """stores sentiment of an item

    Parameters
    ----------
    event: dict, required
        item
        Sentiment

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: application/json

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    if session is None:
        session = operations.get_db_session(is_test, session)

    # Store the sentiment of the item
    sentiment = Sentiment()
    # search for sentiment in database
    str_sentiment = event['Sentiment']
    try:
        sentiment = operations.get_sentiment_by_content_db(str_sentiment, is_test, session)
    except Exception:
        # store sentiment in database
        sentiment.id = str(uuid4())
        sentiment.sentiment = str_sentiment
        try:
            operations.update_object_db(sentiment, is_test, session)
        except Exception as e:
            logger.error("Could not store sentiment. Exception: %s", e, exc_info=True)
            raise
    # store item sentiment in database
    itemsentiment = ItemSentiment()
    # item entity already exists?
    item_id = event['item']['id']
    try:
        itemsentiment = operations.get_itemsentiment_by_sentiment_and_item_db(sentiment.id, item_id, is_test, session)
    except Exception:
        itemsentiment.id = str(uuid4())
        itemsentiment.item_id = item_id
        itemsentiment.sentiment_id = sentiment.id
        try:
            operations.update_object_db(itemsentiment, is_test, session)
        except Exception as e:
            logger.error("Could not store item sentiment. Exception: %s", e, exc_info=True)
            raise


def store_itemphrases(event, context, is_test=False, session=None):
    """stores key phrases of an item

    Parameters
    ----------
    event: dict, required
        item
        KeyPhrases

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: application/json

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    if session is None:
        session = operations.get_db_session(is_test, session)

    # Store all entities of the item
    for str_phrase in event['KeyPhrases']:
        phrase = Keyphrase()
        # search for entity in database
        try:
            phrase = operations.get_phrase_by_content_db(str_phrase, is_test, session)
        except Exception:
            # store phrase in database
            phrase.id = str(uuid4())
            phrase.phrase = str_phrase
            try:
                operations.update_object_db(phrase, is_test, session)
            except Exception as e:
                logger.error("Could not store key phrase. Exception: %s", e, exc_info=True)
                raise
        # store item keyphrase in database
        itemphrase = ItemKeyphrase()
        # item phrase already exists?
        item_id = event['item']['id']
        try:
            itemphrase = operations.get_itemphrase_by_phrase_and_item_db(phrase.id, item_id, is_test, session)
        except Exception:
            itemphrase.id = str(uuid4())
            itemphrase.item_id = item_id
            itemphrase.keyphrase_id = phrase.id
            try:
                operations.update_object_db(itemphrase, is_test, session)
            except Exception as e:
                logger.error("Could not store item key phrase. Exception: %s", e, exc_info=True)
                raise
