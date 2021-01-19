# External imports
import logging
import json
import traceback
from uuid import uuid4
# Helper imports
from core_layer import helper
from core_layer.connection_handler import get_db_session
from core_layer.handler import item_handler, entity_handler, keyphrase_handler
import SearchFactChecks


def get_online_factcheck(event, context, is_test=False, session=None):

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    helper.log_method_initiated(
        "Get online factchecks by item id", event, logger)

    if session is None:
        session = get_db_session(is_test, None)

    try:
        # get id (str) from path
        id = event['pathParameters']['item_id']

        try:
            item = item_handler.get_item_by_id(id, is_test, session)
            if item.language == None:
                raise Exception("Language of Claim not recognized.")
            entity_objects = entity_handler.get_entities_by_itemid(
                id, is_test, session)
            phrase_objects = keyphrase_handler.get_phrases_by_itemid_db(
                id, is_test, session)

            entities = []
            for obj in entity_objects:
                entities.append(obj.to_dict()['entity'])
            phrases = []
            for obj in phrase_objects:
                phrases.append(obj.to_dict()['phrase'])

            sfc_event = {
                "item": item.to_dict(),
                "KeyPhrases": phrases,
                "Entities": entities,
            }
            context = ""

            factcheck = SearchFactChecks.get_FactChecks(sfc_event, context)
            if 'claimReview' in factcheck[0]:
                factcheck_dict = {
                    "id": "0", "url": factcheck[0]['claimReview'][0]['url']}
                if 'title' in factcheck[0]['claimReview'][0]:
                    factcheck_dict["title"] = factcheck[0]['claimReview'][0]['title']
                elif 'textualRating' in factcheck[0]['claimReview'][0]:
                    factcheck_dict["title"] = factcheck[0]['claimReview'][0]['textualRating']
                response = {
                    "statusCode": 200,
                    'headers': {"content-type": "application/json; charset=utf-8"},
                    "body": json.dumps(factcheck_dict)
                }
            else:
                response = {
                    "statusCode": 204,
                    "body": "No factcheck found."
                }

        except Exception:
            response = {
                "statusCode": 404,
                "body": "No factcheck found. Stacktrace: {}".format(traceback.format_exc())
            }

    except Exception:
        response = {
            "statusCode": 400,
            "body": "Could not get item ID. Check HTTP POST payload. Stacktrace: {}".format(traceback.format_exc())
        }

    response_cors = helper.set_cors(response, event, is_test)
    return response_cors
