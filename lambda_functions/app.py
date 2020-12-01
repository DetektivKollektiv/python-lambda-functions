import logging
import json
import os
import boto3
import SearchFactChecks

from datetime import datetime
import requests

from crud import operations, helper, notifications
from crud.model import Item, User, Review, ReviewAnswer, ReviewQuestion, User, Entity, Keyphrase, Sentiment, URL, ItemEntity, ItemKeyphrase, ItemSentiment, ItemURL, Base, Submission, FactChecking_Organization, ExternalFactCheck

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_factcheck_by_itemid(event, context, is_test=False, session=None):

    helper.log_method_initiated("Get factchecks by item id", event, logger)

    if session is None:
        session = operations.get_db_session(is_test, None)

    try:
        # get id (str) from path
        id = event['pathParameters']['item_id']

        try:
            factcheck = operations.get_factcheck_by_itemid_db(
                id, is_test, session)

            if factcheck is None:
                return {
                    "statusCode": 404,
                    "body": "Item or factcheck not found."
                }

            factcheck_dict = factcheck.to_dict()

            response = {
                "statusCode": 200,
                'headers': {"content-type": "application/json; charset=utf-8"},
                "body": json.dumps(factcheck_dict)
            }
        except Exception:
            response = {
                "statusCode": 404,
                "body": "Item or factcheck not found."
            }

    except Exception as e:
        response = {
            "statusCode": 400,
            "body": "Could not get factchecks. Check HTTP POST payload. Exception: {}".format(e)
        }

    response_cors = helper.set_cors(response, event, is_test)
    return response_cors
