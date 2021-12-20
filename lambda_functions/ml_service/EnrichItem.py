import logging
from core_layer.db_handler import Session, update_object

from core_layer.model.item_model import Item
from core_layer.model.external_factcheck_model import ExternalFactCheck
from core_layer.model.factchecking_organization_model import FactChecking_Organization
from core_layer.model.entity_model import Entity, ItemEntity
from core_layer.model.sentiment_model import Sentiment, ItemSentiment
from core_layer.model.keyphrase_model import Keyphrase, ItemKeyphrase
from core_layer.model.claimant_model import Claimant
from core_layer.model.url_model import URL, ItemURL

from core_layer.handler import factchecking_organization_handler, external_factcheck_handler, claimant_handler, url_handler, entity_handler, sentiment_handler, keyphrase_handler, tag_handler

from uuid import uuid4
from urllib.parse import urlparse

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

    with Session() as session:

        # Parse event dict to Item object
        item = Item()
        json_event = event['item']
        for key in json_event:
            setattr(item, key, json_event[key])

        update_object(item, session)


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

    """

    with Session() as session:

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
                organization = factchecking_organization_handler.get_organization_by_name(org_name, session)
            except Exception:
                # store organization in database
                organization.id = str(uuid4())
                organization.name = org_name
                organization.counter_trustworthy = 0
                organization.counter_not_trustworthy = 0
                try:
                    update_object(organization, session)
                except Exception as e:
                    logger.error(
                        "Could not store Organization. Exception: %s", e, exc_info=True)

            factcheck_url = json_event['claimReview'][0]['url']
            factcheck_title = json_event['claimReview'][0]['title']
            item_id = event['item']['id']
            try:
                # Does the factcheck already exist?
                factcheck = external_factcheck_handler.get_factcheck_by_url_and_item_id(
                    factcheck_url, item_id, session)
            except Exception as e:
                # create new factcheck in database
                factcheck.id = str(uuid4())
            # store factcheck in database
            factcheck.url = factcheck_url
            factcheck.title = factcheck_title
            factcheck.item_id = item_id
            factcheck.factchecking_organization_id = organization.id
            try:
                update_object(factcheck, session)
            except Exception as e:
                logger.error(
                    "Could not store factchecks. Exception: %s", e, exc_info=True)
                raise

def store_itementities(event, context):
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

    with Session() as session:

        # Store all entities of the item
        for str_entity in event['Entities']:
            entity = Entity()
            # search for entity in database
            try:
                entity = entity_handler.get_entity_by_content(str_entity, session)
            except Exception:
                # store entity in database
                entity.id = str(uuid4())
                entity.entity = str_entity
                try:
                    update_object(entity, session)
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
                    entity.id, item_id, session)
            except Exception:
                itementity.id = str(uuid4())
                itementity.item_id = item_id
                itementity.entity_id = entity.id
                try:
                    update_object(itementity, session)
                except Exception as e:
                    logger.error(
                        "Could not store item entity. Exception: %s", e, exc_info=True)
                    raise


def store_itemtags(event, context):
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

    with Session() as session:
        # extract item id
        item_id = event['item']['id']

        # Store all tags of the item
        for str_tag in event['Tags']:
            tag_handler.store_tag_for_item(item_id, str_tag, session)


def store_itemsentiment(event, context):
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

    with Session() as session:

        # Store the sentiment of the item
        sentiment = Sentiment()
        # search for sentiment in database
        str_sentiment = event['Sentiment']
        try:
            sentiment = sentiment_handler.get_sentiment_by_content(str_sentiment, session)
        except Exception:
            # store sentiment in database
            sentiment.id = str(uuid4())
            sentiment.sentiment = str_sentiment
            try:
                update_object(sentiment, session)
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
                sentiment.id, item_id, session)
        except Exception:
            itemsentiment.id = str(uuid4())
            itemsentiment.item_id = item_id
            itemsentiment.sentiment_id = sentiment.id
            try:
                update_object(itemsentiment, session)
            except Exception as e:
                logger.error(
                    "Could not store item sentiment. Exception: %s", e, exc_info=True)
                raise


def store_itemphrases(event, context):
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

    with Session() as session:

        # Store all entities of the item
        for str_phrase in event['KeyPhrases']:
            phrase = Keyphrase()
            # search for entity in database
            try:
                phrase = keyphrase_handler.get_phrase_by_content(str_phrase, session)
            except Exception:
                # store phrase in database
                phrase.id = str(uuid4())
                phrase.phrase = str_phrase
                try:
                    update_object(phrase, session)
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
                    phrase.id, item_id, session)
            except Exception:
                itemphrase.id = str(uuid4())
                itemphrase.item_id = item_id
                itemphrase.keyphrase_id = phrase.id
                try:
                    update_object(itemphrase, session)
                except Exception as e:
                    logger.error(
                        "Could not store item key phrase. Exception: %s", e, exc_info=True)
                    raise
