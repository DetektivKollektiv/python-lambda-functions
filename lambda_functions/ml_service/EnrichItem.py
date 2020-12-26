import logging
from core_layer.connection_handler import get_db_session, update_object
from core_layer import helper

from core_layer.model.item_model import Item
from core_layer.model.external_factcheck_model import ExternalFactCheck
from core_layer.model.factchecking_organization_model import FactChecking_Organization
from core_layer.model.entity_model import Entity, ItemEntity
from core_layer.model.tag_model import Tag, ItemTag
from core_layer.model.sentiment_model import Sentiment, ItemSentiment
from core_layer.model.keyphrase_model import Keyphrase, ItemKeyphrase
from core_layer.model.claimant_model import Claimant
from core_layer.model.url_model import URL, ItemURL

from core_layer.handler import factchecking_organization_handler, external_factcheck_handler, claimant_handler, url_handler, entity_handler, sentiment_handler, keyphrase_handler, tag_handler

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
        session = get_db_session(is_test, session)

    # Parse event dict to Item object
    item = Item()
    json_event = event['item']
    for key in json_event:
        setattr(item, key, json_event[key])

    try:
        update_object(item, is_test, session)
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
        session = get_db_session(is_test, session)

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
            organization = factchecking_organization_handler.get_organization_by_name(
                org_name, is_test, session)
        except Exception:
            # store organization in database
            organization.id = str(uuid4())
            organization.name = org_name
            organization.counter_trustworthy = 0
            organization.counter_not_trustworthy = 0
            try:
                update_object(organization, is_test, session)
            except Exception as e:
                logger.error(
                    "Could not store Organization. Exception: %s", e, exc_info=True)

        factcheck_url = json_event['claimReview'][0]['url']
        factcheck_title = json_event['claimReview'][0]['title']
        item_id = event['item']['id']
        try:
            # Does the factcheck already exist?
            factcheck = external_factcheck_handler.get_factcheck_by_url_and_item_id(
                factcheck_url, item_id, is_test, session)
        except Exception as e:
            # create new factcheck in database
            factcheck.id = str(uuid4())
        # store factcheck in database
        factcheck.url = factcheck_url
        factcheck.title = factcheck_title
        factcheck.item_id = item_id
        factcheck.factchecking_organization_id = organization.id
        try:
            update_object(factcheck, is_test, session)
        except Exception as e:
            logger.error(
                "Could not store factchecks. Exception: %s", e, exc_info=True)
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
        session = get_db_session(is_test, session)

    # Store all urls referenced in the item
    for str_url in event['Claim']['urls']:
        if str_url == "":
            continue
        # store claimant derived from url
        domain = urlparse(str_url).hostname
        claimant = Claimant()
        # claimant already exists?
        try:
            claimant = claimant_handler.get_claimant_by_name(
                domain, is_test, session)
        except Exception:
            # store claimant in database
            claimant.id = str(uuid4())
            claimant.claimant = domain
            try:
                update_object(claimant, is_test, session)
            except Exception as e:
                logger.error(
                    "Could not store claimant. Exception: %s", e, exc_info=True)
                raise
        # search for url in database
        url = URL()
        try:
            url = url_handler.get_url_by_content(str_url, is_test, session)
        except Exception:
            # store url in database
            url.id = str(uuid4())
            url.url = str_url
            url.claimant_id = claimant.id
            try:
                update_object(url, is_test, session)
            except Exception as e:
                logger.error("Could not store urls. Exception: %s",
                             e, exc_info=True)
                raise
        itemurl = ItemURL()
        # itemurl already exists?
        item_id = event['item']['id']
        try:
            itemurl = url_handler.get_itemurl_by_url_and_item_id(
                url.id, item_id, is_test, session)
        except Exception:
            # store itemurl in database
            itemurl.id = str(uuid4())
            itemurl.item_id = item_id
            itemurl.url_id = url.id
            try:
                update_object(itemurl, is_test, session)
            except Exception as e:
                logger.error(
                    "Could not store itemurls. Exception: %s", e, exc_info=True)
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
        session = get_db_session(is_test, session)

    # Store all entities of the item
    for str_entity in event['Entities']:
        entity = Entity()
        # search for entity in database
        try:
            entity = entity_handler.get_entity_by_content(
                str_entity, is_test, session)
        except Exception:
            # store entity in database
            entity.id = str(uuid4())
            entity.entity = str_entity
            try:
                update_object(entity, is_test, session)
            except Exception as e:
                logger.error(
                    "Could not store entity. Exception: %s", e, exc_info=True)
                raise
        # store item entity in database
        itementity = ItemEntity()
        # item entity already exists?
        item_id = event['item']['id']
        try:
            itementity = entity_handler.get_itementity_by_entity_and_item_id(
                entity.id, item_id, is_test, session)
        except Exception:
            itementity.id = str(uuid4())
            itementity.item_id = item_id
            itementity.entity_id = entity.id
            try:
                update_object(itementity, is_test, session)
            except Exception as e:
                logger.error(
                    "Could not store item entity. Exception: %s", e, exc_info=True)
                raise


def store_itemtags(event, context, is_test=False, session=None):
    """stores tags of an item

    Parameters
    ----------
    event: dict, required
        item
        Tags

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
        session = get_db_session(is_test, session)

    # Store all entities of the item
    for str_tag in event['Tags']:
        # search for tag in database
        tag = tag_handler.get_tag_by_content(str_tag, is_test, session)
        if tag is None:
            # store tag in database
            tag = Tag()
            tag.id = str(uuid4())
            tag.tag = str_tag
            try:
                update_object(tag, is_test, session)
            except Exception as e:
                logger.error(
                    "Could not store tag. Exception: %s", e, exc_info=True)
                raise
        # item tag already exists?
        item_id = event['item']['id']
        itemtag = tag_handler.get_itemtag_by_tag_and_item_id(tag.id, item_id, is_test, session)
        if itemtag is None:
            # store item tag in database
            itemtag = ItemTag()
            itemtag.id = str(uuid4())
            itemtag.item_id = item_id
            itemtag.tag_id = tag.id
            try:
                update_object(itemtag, is_test, session)
            except Exception as e:
                logger.error(
                    "Could not store item tag. Exception: %s", e, exc_info=True)
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
        session = get_db_session(is_test, session)

    # Store the sentiment of the item
    sentiment = Sentiment()
    # search for sentiment in database
    str_sentiment = event['Sentiment']
    try:
        sentiment = sentiment_handler.get_sentiment_by_content(
            str_sentiment, is_test, session)
    except Exception:
        # store sentiment in database
        sentiment.id = str(uuid4())
        sentiment.sentiment = str_sentiment
        try:
            update_object(sentiment, is_test, session)
        except Exception as e:
            logger.error(
                "Could not store sentiment. Exception: %s", e, exc_info=True)
            raise
    # store item sentiment in database
    itemsentiment = ItemSentiment()
    # item entity already exists?
    item_id = event['item']['id']
    try:
        itemsentiment = sentiment_handler.get_itemsentiment_by_sentiment_and_item_id(
            sentiment.id, item_id, is_test, session)
    except Exception:
        itemsentiment.id = str(uuid4())
        itemsentiment.item_id = item_id
        itemsentiment.sentiment_id = sentiment.id
        try:
            update_object(itemsentiment, is_test, session)
        except Exception as e:
            logger.error(
                "Could not store item sentiment. Exception: %s", e, exc_info=True)
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
        session = get_db_session(is_test, session)

    # Store all entities of the item
    for str_phrase in event['KeyPhrases']:
        phrase = Keyphrase()
        # search for entity in database
        try:
            phrase = keyphrase_handler.get_phrase_by_content(
                str_phrase, is_test, session)
        except Exception:
            # store phrase in database
            phrase.id = str(uuid4())
            phrase.phrase = str_phrase
            try:
                update_object(phrase, is_test, session)
            except Exception as e:
                logger.error(
                    "Could not store key phrase. Exception: %s", e, exc_info=True)
                raise
        # store item keyphrase in database
        itemphrase = ItemKeyphrase()
        # item phrase already exists?
        item_id = event['item']['id']
        try:
            itemphrase = keyphrase_handler.get_itemphrase_by_phrase_and_item_id(
                phrase.id, item_id, is_test, session)
        except Exception:
            itemphrase.id = str(uuid4())
            itemphrase.item_id = item_id
            itemphrase.keyphrase_id = phrase.id
            try:
                update_object(itemphrase, is_test, session)
            except Exception as e:
                logger.error(
                    "Could not store item key phrase. Exception: %s", e, exc_info=True)
                raise
